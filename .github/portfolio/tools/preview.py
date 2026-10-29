"""Local static preview with byte-range responses for seeking video."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import argparse,re,os
ROOT=Path(__file__).resolve().parents[1]
class PreviewHandler(SimpleHTTPRequestHandler):
 def __init__(self,*args,**kwargs):
  self.range_remaining=None;super().__init__(*args,directory=str(ROOT),**kwargs)
 def end_headers(self):
  self.send_header('Cache-Control','no-store, max-age=0');super().end_headers()
 def send_head(self):
  path=Path(self.translate_path(self.path));header=self.headers.get('Range')
  if not header or not path.is_file():return super().send_head()
  m=re.fullmatch(r'bytes=(\d*)-(\d*)',header)
  if not m:return super().send_head()
  size=path.stat().st_size
  start=int(m[1]) if m[1] else max(0,size-int(m[2] or 0));end=min(int(m[2]),size-1) if m[2] and m[1] else size-1
  if start>=size or end<start:
   self.send_response(416);self.send_header('Content-Range',f'bytes */{size}');self.send_header('Content-Length','0');self.end_headers();return None
  f=path.open('rb');f.seek(start);self.range_remaining=end-start+1
  self.send_response(206);self.send_header('Content-Type',self.guess_type(str(path)));self.send_header('Accept-Ranges','bytes');self.send_header('Content-Range',f'bytes {start}-{end}/{size}');self.send_header('Content-Length',str(self.range_remaining));self.end_headers();return f
 def copyfile(self,source,outputfile):
  try:
   if self.range_remaining is None:return super().copyfile(source,outputfile)
   while self.range_remaining:
    data=source.read(min(65536,self.range_remaining))
    if not data:break
    outputfile.write(data);self.range_remaining-=len(data)
  except (BrokenPipeError,ConnectionResetError):pass
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8878);parser.add_argument('--directory',type=Path);args=parser.parse_args()
 if args.directory:ROOT=args.directory.resolve()
 print(f'Local preview: http://127.0.0.1:{args.port}/',flush=True)
 ThreadingHTTPServer(('127.0.0.1',args.port),PreviewHandler).serve_forever()
