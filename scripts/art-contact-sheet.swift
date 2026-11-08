import Foundation
import CoreGraphics
import ImageIO
import CoreText

@main struct ArtContactSheet {
 static func main() throws {
  let folder=URL(fileURLWithPath:CommandLine.arguments[1]);let out=URL(fileURLWithPath:CommandLine.arguments[2]);let w=1100,h=1500
  guard let ctx=CGContext(data:nil,width:w,height:h,bitsPerComponent:8,bytesPerRow:w*4,space:CGColorSpaceCreateDeviceRGB(),bitmapInfo:CGImageAlphaInfo.premultipliedLast.rawValue) else {fatalError("Context")}
  ctx.setFillColor(CGColor(gray:0.055,alpha:1));ctx.fill(CGRect(x:0,y:0,width:w,height:h))
  for k in 0..<25 {
   let i=Int((Double(k)*99/24).rounded());let url=folder.appendingPathComponent(String(format:"frame-%06d.png",i))
   guard let source=CGImageSourceCreateWithURL(url as CFURL,nil),let im=CGImageSourceCreateImageAtIndex(source,0,nil) else {fatalError("Missing frame")}
   let x=(k%5)*220,y=h-(k/5+1)*300
   ctx.draw(im,in:CGRect(x:x,y:y+24,width:220,height:275))
   let caption=String(format:"FRAME %03d   %.2fs",i+1,Double(i)/30)
   let font=CTFontCreateWithName("Menlo" as CFString,11,nil)
   let at=NSAttributedString(string:caption,attributes:[NSAttributedString.Key(kCTFontAttributeName as String):font,NSAttributedString.Key(kCTForegroundColorAttributeName as String):CGColor(gray:0.85,alpha:1)])
   ctx.textPosition=CGPoint(x:x+8,y:y+8);CTLineDraw(CTLineCreateWithAttributedString(at),ctx)
  }
  guard let im=ctx.makeImage(),let dest=CGImageDestinationCreateWithURL(out as CFURL,"public.png" as CFString,1,nil) else {fatalError("Output")}
  CGImageDestinationAddImage(dest,im,nil);guard CGImageDestinationFinalize(dest) else {fatalError("Write")}
 }
}
