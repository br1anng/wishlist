import http from 'node:http';
import {readFile,readdir} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
const root=fileURLToPath(new URL('.',import.meta.url));
const routes={'/':'index.html','/app.js':'app.js','/style.css':'style.css'};
for(const file of await readdir(root+'assets/products'))if(/^[a-z0-9-]+\.(png|jpe?g|webp)$/i.test(file))routes['/assets/products/'+file]='assets/products/'+file;
const types={html:'text/html; charset=utf-8',js:'text/javascript; charset=utf-8',css:'text/css; charset=utf-8',jpg:'image/jpeg',png:'image/png',webp:'image/webp'};
http.createServer(async(req,res)=>{
 const file=routes[new URL(req.url,'http://localhost').pathname];
 if(!file){res.writeHead(404);return res.end('Not found');}
 try{const data=await readFile(root+file);res.writeHead(200,{'Content-Type':types[file.split('.').pop()],'X-Content-Type-Options':'nosniff'});res.end(data);}
 catch{res.writeHead(500);res.end('Unable to load page');}
}).listen(Number(process.env.PORT)||3000,'0.0.0.0',()=>console.log('Wishlist running on port '+(process.env.PORT||3000)));
