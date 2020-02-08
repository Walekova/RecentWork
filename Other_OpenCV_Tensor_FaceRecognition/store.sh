sudo apt-get update
apt-get install automake autotools-dev g++ git libcurl4-openssl-dev libfuse-dev libssl-dev libxml2-dev make pkg-config
git clone https://github.com/s3fs-fuse/s3fs-fuse.git
cd s3fs-fuse 
 ./autogen.sh 
 ./configure
make

make install
echo "b692164e4ad242d484a581ea866a8015:73f931711b0b5182b3e4845ac3726a0ab4ee0512f421d86c"  > $HOME/.cos_creds

chmod 600 $HOME/.cos_creds
mkdir /mnt/mybucket
s3fs cos.deeplearning.walekova /mnt/mybucket -o passwd_file=$HOME/.cos_creds -o sigv2 -o use_path_request_style -o url=https://s3.eu-gb.cloud-object-storage.appdomain.cloud

