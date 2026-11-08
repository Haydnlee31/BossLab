import Foundation
import AVFoundation
import CoreGraphics
import ImageIO
import CoreVideo

enum CaptureError: Error { case invalidArguments, invalidFrame(String), writer(String), timeout }

@main
struct EncodeUnrealVideo {
    static func main() async throws {
        guard CommandLine.arguments.count == 3 else { throw CaptureError.invalidArguments }
        let directory = URL(fileURLWithPath: CommandLine.arguments[1], isDirectory: true)
        let output = URL(fileURLWithPath: CommandLine.arguments[2])
        let frames = try FileManager.default.contentsOfDirectory(at: directory, includingPropertiesForKeys: nil)
            .filter { $0.pathExtension == "png" }.sorted { $0.lastPathComponent < $1.lastPathComponent }
        guard let first = frames.first, let source = CGImageSourceCreateWithURL(first as CFURL, nil),
              let initial = CGImageSourceCreateImageAtIndex(source, 0, nil), frames.count >= 2 else {
            throw CaptureError.invalidFrame("No complete frame sequence")
        }
        let width = initial.width, height = initial.height
        let writer = try AVAssetWriter(outputURL: output, fileType: .mp4)
        let input = AVAssetWriterInput(mediaType: .video, outputSettings: [
            AVVideoCodecKey: AVVideoCodecType.h264, AVVideoWidthKey: width, AVVideoHeightKey: height,
            AVVideoCompressionPropertiesKey: [AVVideoAverageBitRateKey: 6_000_000]
        ])
        input.expectsMediaDataInRealTime = false
        let adaptor = AVAssetWriterInputPixelBufferAdaptor(assetWriterInput: input, sourcePixelBufferAttributes: [
            kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32ARGB,
            kCVPixelBufferWidthKey as String: width, kCVPixelBufferHeightKey as String: height,
            kCVPixelBufferCGImageCompatibilityKey as String: true,
            kCVPixelBufferCGBitmapContextCompatibilityKey as String: true
        ])
        guard writer.canAdd(input) else { throw CaptureError.writer("Cannot add video track") }
        writer.add(input)
        guard writer.startWriting() else { throw CaptureError.writer(String(describing: writer.error)) }
        writer.startSession(atSourceTime: .zero)
        for (index, url) in frames.enumerated() {
            let deadline = Date().addingTimeInterval(15)
            while !input.isReadyForMoreMediaData {
                guard Date() < deadline, writer.status == .writing else { throw CaptureError.timeout }
                try await Task.sleep(for: .milliseconds(5))
            }
            try autoreleasepool {
                guard let src = CGImageSourceCreateWithURL(url as CFURL, nil),
                      let frame = CGImageSourceCreateImageAtIndex(src, 0, nil),
                      frame.width == width, frame.height == height,
                      let pool = adaptor.pixelBufferPool else { throw CaptureError.invalidFrame(url.path) }
                var optionalBuffer: CVPixelBuffer?
                guard CVPixelBufferPoolCreatePixelBuffer(nil, pool, &optionalBuffer) == kCVReturnSuccess,
                      let buffer = optionalBuffer else { throw CaptureError.writer("Pixel buffer allocation") }
                CVPixelBufferLockBaseAddress(buffer, [])
                defer { CVPixelBufferUnlockBaseAddress(buffer, []) }
                guard let context = CGContext(data: CVPixelBufferGetBaseAddress(buffer), width: width, height: height,
                    bitsPerComponent: 8, bytesPerRow: CVPixelBufferGetBytesPerRow(buffer),
                    space: CGColorSpaceCreateDeviceRGB(), bitmapInfo: CGImageAlphaInfo.noneSkipFirst.rawValue) else {
                    throw CaptureError.writer("Bitmap context allocation")
                }
                context.draw(frame, in: CGRect(x: 0, y: 0, width: width, height: height))
                guard adaptor.append(buffer, withPresentationTime: CMTime(value: Int64(index), timescale: 30)) else {
                    throw CaptureError.writer(String(describing: writer.error))
                }
            }
        }
        input.markAsFinished()
        await writer.finishWriting()
        guard writer.status == .completed else { throw CaptureError.writer(String(describing: writer.error)) }
        let asset = AVURLAsset(url: output)
        let duration = try await asset.load(.duration)
        let tracks = try await asset.loadTracks(withMediaType: .video)
        guard tracks.count == 1, abs(duration.seconds - Double(frames.count)/30) < 0.05 else {
            throw CaptureError.writer("Encoded duration/track verification failed")
        }
        let metadata: [String: Any] = ["kind": "Actual Unreal engine frame sequence, fixed timestep; not a real-time FPS measurement", "frames": frames.count, "fps": 30, "width": width, "height": height, "seconds": duration.seconds, "audio": false, "output": output.path]
        let data = try JSONSerialization.data(withJSONObject: metadata, options: [.prettyPrinted, .sortedKeys])
        try data.write(to: output.deletingPathExtension().appendingPathExtension("json"))
        FileHandle.standardOutput.write(data)
    }
}
