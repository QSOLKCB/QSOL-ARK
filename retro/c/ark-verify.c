/* SPDX-License-Identifier: Apache-2.0 */
#include <stdint.h>
#include <stdio.h>
#include <string.h>

typedef struct {
    uint32_t h[8];
    uint64_t bits;
    unsigned char block[64];
    size_t used;
} sha256_ctx;

static uint32_t rotr(uint32_t x, unsigned n) { return (x >> n) | (x << (32u - n)); }

static void transform(sha256_ctx *c, const unsigned char block[64]) {
    static const uint32_t k[64] = {
        0x428a2f98u,0x71374491u,0xb5c0fbcfu,0xe9b5dba5u,0x3956c25bu,0x59f111f1u,0x923f82a4u,0xab1c5ed5u,
        0xd807aa98u,0x12835b01u,0x243185beu,0x550c7dc3u,0x72be5d74u,0x80deb1feu,0x9bdc06a7u,0xc19bf174u,
        0xe49b69c1u,0xefbe4786u,0x0fc19dc6u,0x240ca1ccu,0x2de92c6fu,0x4a7484aau,0x5cb0a9dcu,0x76f988dau,
        0x983e5152u,0xa831c66du,0xb00327c8u,0xbf597fc7u,0xc6e00bf3u,0xd5a79147u,0x06ca6351u,0x14292967u,
        0x27b70a85u,0x2e1b2138u,0x4d2c6dfcu,0x53380d13u,0x650a7354u,0x766a0abbu,0x81c2c92eu,0x92722c85u,
        0xa2bfe8a1u,0xa81a664bu,0xc24b8b70u,0xc76c51a3u,0xd192e819u,0xd6990624u,0xf40e3585u,0x106aa070u,
        0x19a4c116u,0x1e376c08u,0x2748774cu,0x34b0bcb5u,0x391c0cb3u,0x4ed8aa4au,0x5b9cca4fu,0x682e6ff3u,
        0x748f82eeu,0x78a5636fu,0x84c87814u,0x8cc70208u,0x90befffau,0xa4506cebu,0xbef9a3f7u,0xc67178f2u
    };
    uint32_t w[64], a,b,d,e,f,g,h,t1,t2,cc;
    unsigned i;
    for (i=0;i<16;i++)
        w[i] = ((uint32_t)block[i*4]<<24)|((uint32_t)block[i*4+1]<<16)|((uint32_t)block[i*4+2]<<8)|block[i*4+3];
    for (i=16;i<64;i++) {
        uint32_t s0=rotr(w[i-15],7)^rotr(w[i-15],18)^(w[i-15]>>3);
        uint32_t s1=rotr(w[i-2],17)^rotr(w[i-2],19)^(w[i-2]>>10);
        w[i]=w[i-16]+s0+w[i-7]+s1;
    }
    a=c->h[0]; b=c->h[1]; cc=c->h[2]; d=c->h[3]; e=c->h[4]; f=c->h[5]; g=c->h[6]; h=c->h[7];
    for (i=0;i<64;i++) {
        uint32_t S1=rotr(e,6)^rotr(e,11)^rotr(e,25);
        uint32_t ch=(e&f)^((~e)&g);
        uint32_t S0=rotr(a,2)^rotr(a,13)^rotr(a,22);
        uint32_t maj=(a&b)^(a&cc)^(b&cc);
        t1=h+S1+ch+k[i]+w[i]; t2=S0+maj;
        h=g; g=f; f=e; e=d+t1; d=cc; cc=b; b=a; a=t1+t2;
    }
    c->h[0]+=a; c->h[1]+=b; c->h[2]+=cc; c->h[3]+=d; c->h[4]+=e; c->h[5]+=f; c->h[6]+=g; c->h[7]+=h;
}

static void init(sha256_ctx *c) {
    static const uint32_t iv[8]={0x6a09e667u,0xbb67ae85u,0x3c6ef372u,0xa54ff53au,0x510e527fu,0x9b05688cu,0x1f83d9abu,0x5be0cd19u};
    memcpy(c->h,iv,sizeof(iv)); c->bits=0; c->used=0;
}

static void update(sha256_ctx *c, const unsigned char *p, size_t n) {
    while (n) {
        size_t take=64-c->used; if (take>n) take=n;
        memcpy(c->block+c->used,p,take); c->used+=take; p+=take; n-=take; c->bits+=(uint64_t)take*8u;
        if (c->used==64) { transform(c,c->block); c->used=0; }
    }
}

static void final(sha256_ctx *c, unsigned char out[32]) {
    unsigned i;
    c->block[c->used++]=0x80;
    if (c->used>56) { while(c->used<64) c->block[c->used++]=0; transform(c,c->block); c->used=0; }
    while(c->used<56) c->block[c->used++]=0;
    for(i=0;i<8;i++) c->block[63-i]=(unsigned char)(c->bits>>(i*8));
    transform(c,c->block);
    for(i=0;i<8;i++){ out[i*4]=(unsigned char)(c->h[i]>>24); out[i*4+1]=(unsigned char)(c->h[i]>>16); out[i*4+2]=(unsigned char)(c->h[i]>>8); out[i*4+3]=(unsigned char)c->h[i]; }
}

static int hash_file(const char *path, char hex[65]) {
    FILE *f=fopen(path,"rb"); unsigned char buf[4096], digest[32]; size_t n; sha256_ctx c; unsigned i;
    if(!f){ perror(path); return 2; }
    init(&c); while((n=fread(buf,1,sizeof(buf),f))>0) update(&c,buf,n);
    if(ferror(f)){ perror("read"); fclose(f); return 2; } fclose(f); final(&c,digest);
    for (i=0;i<32;i++) { sprintf(hex+i*2,"%02x",digest[i]); }
    hex[64]='\0';
    return 0;
}

int main(int argc, char **argv) {
    char hex[65]; int rc;
    if(argc!=2 && argc!=3){ fprintf(stderr,"usage: %s FILE [EXPECTED_SHA256]\n",argv[0]); return 2; }
    rc=hash_file(argv[1],hex); if(rc) return rc;
    puts(hex);
    if(argc==3 && strcmp(hex,argv[2])!=0){ fprintf(stderr,"ARK_HASH_MISMATCH expected=%s actual=%s\n",argv[2],hex); return 1; }
    if(argc==3) puts("ARK_HASH_OK");
    return 0;
}
