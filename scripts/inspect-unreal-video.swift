import Foundation
import AVFoundation
import CoreImage
import ImageIO

@main
struct InspectVideo {
    static func main() async throws {
        let url=URL(fileURLWithPath: CommandLine.arguments[1])
        let asset=AVURLAsset(url:url)
        let tracks=try await asset.loadTracks(withMediaType:.video)
        guard let track=tracks.first else { throw NSError(domain:"MissingVideo",code:1) }
        let reader=try AVAssetReader(asset:asset)
        let output=AVAssetReaderTrackOutput(track:track,outputSettings:[kCVPixelBufferPixelFormatTypeKey as String:kCVPixelFormatType_32BGRA])
        reader.add(output)
        guard reader.startReading() else { throw reader.error ?? NSError(domain:"Decode",code:1) }
        var count=0
        while let sample=output.copyNextSampleBuffer() {
            if count==90, let buffer=CMSampleBufferGetImageBuffer(sample) {
                let image=CIImage(cvPixelBuffer:buffer)
                let context=CIContext()
                guard let cg=context.createCGImage(image,from:image.extent),
                      let destination=CGImageDestinationCreateWithURL(url.deletingPathExtension().appendingPathExtension("png") as CFURL,"public.png" as CFString,1,nil) else { throw NSError(domain:"Poster",code:1) }
                CGImageDestinationAddImage(destination,cg,nil)
                guard CGImageDestinationFinalize(destination) else { throw NSError(domain:"Poster",code:2) }
            }
            count += 1
        }
        guard reader.status == .completed, count==(CommandLine.arguments.count>2 ? Int(CommandLine.arguments[2])! : 180) else { throw reader.error ?? NSError(domain:"FrameCount",code:count) }
        let result="{\"decoded_frames\":\(count),\"status\":\"completed\",\"poster_frame\":90}"
        try result.write(to:url.deletingPathExtension().appendingPathExtension("decode.json"),atomically:true,encoding:.utf8)
        FileHandle.standardOutput.write(Data(result.utf8))
    }
}
