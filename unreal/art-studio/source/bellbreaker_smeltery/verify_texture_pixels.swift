import Foundation
import ImageIO
import CoreGraphics
let dir=CommandLine.arguments[1]
func pixels(_ path:String)->[UInt8] {
 let src=CGImageSourceCreateWithURL(URL(fileURLWithPath:path) as CFURL,nil)!
 let im=CGImageSourceCreateImageAtIndex(src,0,nil)!
 var a=[UInt8](repeating:0,count:im.width*im.height*4)
 a.withUnsafeMutableBytes { b in
  let c=CGContext(data:b.baseAddress,width:im.width,height:im.height,bitsPerComponent:8,bytesPerRow:im.width*4,space:CGColorSpace(name:CGColorSpace.sRGB)!,bitmapInfo:CGImageAlphaInfo.premultipliedLast.rawValue)!
  c.draw(im,in:CGRect(x:0,y:0,width:im.width,height:im.height))
 }
 return a
}
var rows=[[String:Any]]()
for name in try FileManager.default.contentsOfDirectory(atPath:dir).filter({$0.hasSuffix(".source-webp")}).sorted(){
 let old=dir+"/"+name;let new=String(old.dropLast(".source-webp".count))+".png";let a=pixels(old),b=pixels(new)
 var maxd=0;var changed=0
 for i in a.indices {let d=abs(Int(a[i])-Int(b[i]));maxd=max(maxd,d);if d>0{changed+=1}}
 rows.append(["file":name,"rgba_channel_count":a.count,"changed_channels":changed,"max_byte_difference":maxd])
}
let d=try JSONSerialization.data(withJSONObject:rows,options:.prettyPrinted);print(String(data:d,encoding:.utf8)!)
