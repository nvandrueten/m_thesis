/*
DES implemenation.
(DES implementation used in research)

DES encryption is based on: https://github.com/lbeatu/The-TRIPLE-DES-Algorithm-Illustrated-for-C-code.
This version has been modified to run on a riscv processor.
*/
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

static char IP[] = {
    58, 50, 42, 34, 26, 18, 10,  2,
    60, 52, 44, 36, 28, 20, 12,  4,
    62, 54, 46, 38, 30, 22, 14,  6,
    64, 56, 48, 40, 32, 24, 16,  8,
    57, 49, 41, 33, 25, 17,  9,  1,
    59, 51, 43, 35, 27, 19, 11,  3,
    61, 53, 45, 37, 29, 21, 13,  5,
    63, 55, 47, 39, 31, 23, 15,  7
};

static char PI[] = {
    40,  8, 48, 16, 56, 24, 64, 32,
    39,  7, 47, 15, 55, 23, 63, 31,
    38,  6, 46, 14, 54, 22, 62, 30,
    37,  5, 45, 13, 53, 21, 61, 29,
    36,  4, 44, 12, 52, 20, 60, 28,
    35,  3, 43, 11, 51, 19, 59, 27,
    34,  2, 42, 10, 50, 18, 58, 26,
    33,  1, 41,  9, 49, 17, 57, 25
};

static char E[] = {
    32,  1,  2,  3,  4,  5,
     4,  5,  6,  7,  8,  9,
     8,  9, 10, 11, 12, 13,
    12, 13, 14, 15, 16, 17,
    16, 17, 18, 19, 20, 21,
    20, 21, 22, 23, 24, 25,
    24, 25, 26, 27, 28, 29,
    28, 29, 30, 31, 32,  1
};

static char P[] = {
    16,  7, 20, 21,
    29, 12, 28, 17,
     1, 15, 23, 26,
     5, 18, 31, 10,
     2,  8, 24, 14,
    32, 27,  3,  9,
    19, 13, 30,  6,
    22, 11,  4, 25
};

static char S[8][64] = {{
    /* S1 */
    14,  4, 13,  1,  2, 15, 11,  8,  3, 10,  6, 12,  5,  9,  0,  7,
     0, 15,  7,  4, 14,  2, 13,  1, 10,  6, 12, 11,  9,  5,  3,  8,
     4,  1, 14,  8, 13,  6,  2, 11, 15, 12,  9,  7,  3, 10,  5,  0,
    15, 12,  8,  2,  4,  9,  1,  7,  5, 11,  3, 14, 10,  0,  6, 13
},{
    /* S2 */
    15,  1,  8, 14,  6, 11,  3,  4,  9,  7,  2, 13, 12,  0,  5, 10,
     3, 13,  4,  7, 15,  2,  8, 14, 12,  0,  1, 10,  6,  9, 11,  5,
     0, 14,  7, 11, 10,  4, 13,  1,  5,  8, 12,  6,  9,  3,  2, 15,
    13,  8, 10,  1,  3, 15,  4,  2, 11,  6,  7, 12,  0,  5, 14,  9
},{
    /* S3 */
    10,  0,  9, 14,  6,  3, 15,  5,  1, 13, 12,  7, 11,  4,  2,  8,
    13,  7,  0,  9,  3,  4,  6, 10,  2,  8,  5, 14, 12, 11, 15,  1,
    13,  6,  4,  9,  8, 15,  3,  0, 11,  1,  2, 12,  5, 10, 14,  7,
     1, 10, 13,  0,  6,  9,  8,  7,  4, 15, 14,  3, 11,  5,  2, 12
},{
    /* S4 */
     7, 13, 14,  3,  0,  6,  9, 10,  1,  2,  8,  5, 11, 12,  4, 15,
    13,  8, 11,  5,  6, 15,  0,  3,  4,  7,  2, 12,  1, 10, 14,  9,
    10,  6,  9,  0, 12, 11,  7, 13, 15,  1,  3, 14,  5,  2,  8,  4,
     3, 15,  0,  6, 10,  1, 13,  8,  9,  4,  5, 11, 12,  7,  2, 14
},{
    /* S5 */
     2, 12,  4,  1,  7, 10, 11,  6,  8,  5,  3, 15, 13,  0, 14,  9,
    14, 11,  2, 12,  4,  7, 13,  1,  5,  0, 15, 10,  3,  9,  8,  6,
     4,  2,  1, 11, 10, 13,  7,  8, 15,  9, 12,  5,  6,  3,  0, 14,
    11,  8, 12,  7,  1, 14,  2, 13,  6, 15,  0,  9, 10,  4,  5,  3
},{
    /* S6 */
    12,  1, 10, 15,  9,  2,  6,  8,  0, 13,  3,  4, 14,  7,  5, 11,
    10, 15,  4,  2,  7, 12,  9,  5,  6,  1, 13, 14,  0, 11,  3,  8,
     9, 14, 15,  5,  2,  8, 12,  3,  7,  0,  4, 10,  1, 13, 11,  6,
     4,  3,  2, 12,  9,  5, 15, 10, 11, 14,  1,  7,  6,  0,  8, 13
},{
    /* S7 */
     4, 11,  2, 14, 15,  0,  8, 13,  3, 12,  9,  7,  5, 10,  6,  1,
    13,  0, 11,  7,  4,  9,  1, 10, 14,  3,  5, 12,  2, 15,  8,  6,
     1,  4, 11, 13, 12,  3,  7, 14, 10, 15,  6,  8,  0,  5,  9,  2,
     6, 11, 13,  8,  1,  4, 10,  7,  9,  5,  0, 15, 14,  2,  3, 12
},{
    /* S8 */
    13,  2,  8,  4,  6, 15, 11,  1, 10,  9,  3, 14,  5,  0, 12,  7,
     1, 15, 13,  8, 10,  3,  7,  4, 12,  5,  6, 11,  0, 14,  9,  2,
     7, 11,  4,  1,  9, 12, 14,  2,  0,  6, 10, 13, 15,  3,  5,  8,
     2,  1, 14,  7,  4, 10,  8, 13, 15, 12,  9,  0,  3,  5,  6, 11
}};

static char PC1[] = {
    57, 49, 41, 33, 25, 17,  9,
     1, 58, 50, 42, 34, 26, 18,
    10,  2, 59, 51, 43, 35, 27,
    19, 11,  3, 60, 52, 44, 36,

    63, 55, 47, 39, 31, 23, 15,
     7, 62, 54, 46, 38, 30, 22,
    14,  6, 61, 53, 45, 37, 29,
    21, 13,  5, 28, 20, 12,  4
};

static char PC2[] = {
    14, 17, 11, 24,  1,  5,
     3, 28, 15,  6, 21, 10,
    23, 19, 12,  4, 26,  8,
    16,  7, 27, 20, 13,  2,
    41, 52, 31, 37, 47, 55,
    30, 40, 51, 45, 33, 48,
    44, 49, 39, 56, 34, 53,
    46, 42, 50, 36, 29, 32
};

static char iteration_shift[] = {
/* 1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16 */
1,  1,  2,  2,  2,  2,  2,  2,  1,  2,  2,  2,  2,  2,  2,  1
};

#if OFFLINE
void write_value(char file_name[], char value) {
  char content[256];
  sprintf(content, "%d\n", value);
  FILE *pFile = fopen(file_name, "a");
  fprintf(pFile, content);
  fclose(pFile);
}

void write_row(unsigned char row) {
	write_value("des2_row_oracle.txt", row);
}

void write_column(unsigned char column) {
	write_value("des2_column_oracle.txt", column);
}

void write_sbox(unsigned char sbox) {
	write_value("des2_sbox_oracle.txt", sbox);
}

void write_and(unsigned char and) {
	write_value("des2_and_oracle.txt", and);
}

void write_or(unsigned char or) {
	write_value("des2_or_oracle.txt", or);
}

void write_ro(unsigned char ro) {
	write_value("des2_roundoutput_oracle.txt", ro);
}

#endif

uint64_t des(uint64_t input, uint64_t key) {
  int i, j;

  /* 8 bit */
  char row, column;

  /* 28 bits */
  uint32_t C                  = 0;
  uint32_t D                  = 0;

  /* 32 bit */
  uint32_t L                  = 0;
  uint32_t R                  = 0;
  uint32_t s_output           = 0;
  uint32_t f_function_res     = 0;
  uint32_t temp               = 0;

  /* 48 bit */
  uint64_t sub_key[16]        = {0};
  uint64_t s_input            = 0;

  /* 56 bit */
  uint64_t permuted_choice_1  = 0;
  uint64_t permuted_choice_2  = 0;

  /* 64 bit */
  uint64_t init_perm_res      = 0;
  uint64_t inv_init_perm_res  = 0;
  uint64_t pre_output         = 0;

  /* initial permutation */
  for (i = 0; i < 64; i++) {
    init_perm_res <<= 1;
    init_perm_res |= (input >> (64-IP[i])) & 0x0000000000000001;
  }
  L = (uint32_t) (init_perm_res >> 32) & 0x00000000ffffffff;
  R = (uint32_t) init_perm_res & 0x00000000ffffffff;

  for (i = 0; i < 56; i++) {
    permuted_choice_1 <<= 1;//
    permuted_choice_1 |= (key >> (64-PC1[i])) & 0x0000000000000001;
  }

  C = (uint32_t) ((permuted_choice_1 >> 28) & 0x000000000fffffff);
  D = (uint32_t) (permuted_choice_1 & 0x000000000fffffff);

  for (i = 0; i< 16; i++) {
    for (j = 0; j < iteration_shift[i]; j++) {
      C = (0x0fffffff & (C << 1)) | (0x00000001 & (C >> 27));
      D = (0x0fffffff & (D << 1)) | (0x00000001 & (D >> 27));
    }
    permuted_choice_2 = 0;
    permuted_choice_2 = (((uint64_t) C) << 28) | (uint64_t) D ;

    sub_key[i] = 0;
    for (j = 0; j < 48; j++) {
      sub_key[i] <<= 1;
      sub_key[i] |= (permuted_choice_2 >> (56-PC2[j])) & 0x0000000000000001;
    }
  }

  for (i = 0; i < 16; i++) {
    s_input = 0;
    for (j = 0; j< 48; j++) {
      s_input <<= 1;
      s_input |= (uint64_t) ((R >> (32-E[j])) & 0x00000001);

    }
    s_input = s_input ^ sub_key[i];
    for (j = 0; j < 8; j++) {
      row = (char) ((s_input & (0x0000840000000000 >> 6*j)) >> (42-6*j));
      row = (row >> 4) | (row & 0x01);

      column = (char) ((s_input & (0x0000780000000000 >> 6*j)) >> (43-6*j));

      s_output <<= 4;
      #if OFFLINE
      if (i == 0 && j == 0) {
        write_row(row);
        write_column(column);
        write_sbox((uint32_t) S[j][16*row + column]);
        write_and((uint32_t) S[j][16*row + column] & 0x0f);
        printf("sbox: %d\n", (uint32_t) (S[j][16*row + column]));
        printf("sbox: %d\n", (S[j][16*row + column]));
        printf("sbox and : %d\n", (S[j][16*row + column] & 0x0f));

        write_or(s_output | (uint32_t) (S[j][16*row + column] & 0x0f));
      }
      #endif
      s_output |= (uint32_t) (S[j][16*row + column] & 0x0f);
    }
    f_function_res = 0;
    for (j = 0; j < 32; j++) {
      f_function_res <<= 1;
      f_function_res |= (s_output >> (32 - P[j])) & 0x00000001;
    }
    temp = R;
    R = L ^ f_function_res;
    L = temp;

    #if FIRSTROUNDONLY
      if (i == 0) {
          break;
      }
    #endif
  }
  pre_output = (((uint64_t) R) << 32) | (uint64_t) L;

  for (i = 0; i < 64; i++) {
    inv_init_perm_res <<= 1;
    inv_init_perm_res |= (pre_output >> (64-PI[i])) & 0x0000000000000001;
  }
  return inv_init_perm_res;
}

int main() {
  uint64_t key = 0x133457799BBCDFF1;
  #if TVLA_FIXED
  uint64_t input = 0xda39a3ee5e6b4b0d;
  #elif TVLA_RANDOM || SVF
    #if RUN==0
    uint64_t input = 0xedfdf6a57a43eb8c;
    #endif
    #if RUN==1
    uint64_t input = 0x3f522522788d1f52;
    #endif
    #if RUN==2
    uint64_t input = 0x6351ec3195561f2f;
    #endif
    #if RUN==3
    uint64_t input = 0xe8a24dedc2f1a124;
    #endif
    #if RUN==4
    uint64_t input = 0x49f4085e5c84ea8;
    #endif
    #if RUN==5
    uint64_t input = 0x198bcbb6e84fe65;
    #endif
    #if RUN==6
    uint64_t input = 0x218381878f9f31c5;
    #endif
    #if RUN==7
    uint64_t input = 0xd73cdc4e1dd23ebf;
    #endif
    #if RUN==8
    uint64_t input = 0xcee82be5a615e41d;
    #endif
    #if RUN==9
    uint64_t input = 0x9ee9f1d3ae605e49;
    #endif
    #if RUN==10
    uint64_t input = 0x81f7ee76e5ae2096;
    #endif
    #if RUN==11
    uint64_t input = 0x2c6db1f71dd083e7;
    #endif
    #if RUN==12
    uint64_t input = 0x15ffd72c90e9d2ba;
    #endif
    #if RUN==13
    uint64_t input = 0xe9a12720be2f0ae;
    #endif
    #if RUN==14
    uint64_t input = 0xe6c567d4a2e1e0ac;
    #endif
    #if RUN==15
    uint64_t input = 0x58bb5b7a7f01167;
    #endif
    #if RUN==16
    uint64_t input = 0xef1cb25f50567a60;
    #endif
    #if RUN==17
    uint64_t input = 0xd420d441e7e155d9;
    #endif
    #if RUN==18
    uint64_t input = 0x207e30f372df971;
    #endif
    #if RUN==19
    uint64_t input = 0x2f16505047449cfa;
    #endif
    #if RUN==20
    uint64_t input = 0xf355cee0908eaa;
    #endif
    #if RUN==21
    uint64_t input = 0xca523b2bba41b07e;
    #endif
    #if RUN==22
    uint64_t input = 0x882eeecf81f57e74;
    #endif
    #if RUN==23
    uint64_t input = 0xd5662f54da55fb;
    #endif
    #if RUN==24
    uint64_t input = 0x39388ee08cbce292;
    #endif
    #if RUN==25
    uint64_t input = 0x348d4b5ae6d45256;
    #endif
    #if RUN==26
    uint64_t input = 0x73864275b6756aa;
    #endif
    #if RUN==27
    uint64_t input = 0x782353829ffcf1a4;
    #endif
    #if RUN==28
    uint64_t input = 0xb46335398387127;
    #endif
    #if RUN==29
    uint64_t input = 0x7754ea6315908537;
    #endif
    #if RUN==30
    uint64_t input = 0x5c94e378a64e3e;
    #endif
    #if RUN==31
    uint64_t input = 0x4bc65e8242321b9;
    #endif
    #if RUN==32
    uint64_t input = 0xb3613c318a7ab04b;
    #endif
    #if RUN==33
    uint64_t input = 0xea3bb97926f4855;
    #endif
    #if RUN==34
    uint64_t input = 0x71ad4cf0a1c9b7df;
    #endif
    #if RUN==35
    uint64_t input = 0x943ab1391da4f865;
    #endif
    #if RUN==36
    uint64_t input = 0xf9ff741536318cbf;
    #endif
    #if RUN==37
    uint64_t input = 0xb3607b562b81ca71;
    #endif
    #if RUN==38
    uint64_t input = 0x53a356e2d4c4b4;
    #endif
    #if RUN==39
    uint64_t input = 0x1686889b5555e82;
    #endif
    #if RUN==40
    uint64_t input = 0xf2b9e247bcd872c2;
    #endif
    #if RUN==41
    uint64_t input = 0x51f6e36eb0415c57;
    #endif
    #if RUN==42
    uint64_t input = 0xcae6e9de8381a0b7;
    #endif
    #if RUN==43
    uint64_t input = 0x61c2d233e74b647b;
    #endif
    #if RUN==44
    uint64_t input = 0xa848319cd442831e;
    #endif
    #if RUN==45
    uint64_t input = 0xe5b2b25dbdf159b;
    #endif
    #if RUN==46
    uint64_t input = 0xa0d368b010fac0f2;
    #endif
    #if RUN==47
    uint64_t input = 0x48be838b57afe67;
    #endif
    #if RUN==48
    uint64_t input = 0xc7f5c7258375c3e8;
    #endif
    #if RUN==49
    uint64_t input = 0xea6e71111cf02ad1;
    #endif
    #if RUN==50
    uint64_t input = 0xe169133bec6a96d9;
    #endif
    #if RUN==51
    uint64_t input = 0x619216ba627af77e;
    #endif
    #if RUN==52
    uint64_t input = 0x40643ce316fb7d4;
    #endif
    #if RUN==53
    uint64_t input = 0x10db5f60c4da8a24;
    #endif
    #if RUN==54
    uint64_t input = 0x1a18aeada67e8cb7;
    #endif
    #if RUN==55
    uint64_t input = 0xce1bb15429f90bd;
    #endif
    #if RUN==56
    uint64_t input = 0x60150e47eeaca3c;
    #endif
    #if RUN==57
    uint64_t input = 0x10c2899161b2dd1;
    #endif
    #if RUN==58
    uint64_t input = 0xc7caf63d1432b65f;
    #endif
    #if RUN==59
    uint64_t input = 0x390e7a9937937d3;
    #endif
    #if RUN==60
    uint64_t input = 0x6bc6405b4ecf3d4d;
    #endif
    #if RUN==61
    uint64_t input = 0xc75e6ead85d8ee74;
    #endif
    #if RUN==62
    uint64_t input = 0x46924543c79ec35a;
    #endif
    #if RUN==63
    uint64_t input = 0xb3f29897b55d26b6;
    #endif
    #if RUN==64
    uint64_t input = 0x70a4e62273574e9;
    #endif
    #if RUN==65
    uint64_t input = 0x3a64264dba71587;
    #endif
    #if RUN==66
    uint64_t input = 0x86765b71b3c1e3;
    #endif
    #if RUN==67
    uint64_t input = 0x4f98d64fb4542b7c;
    #endif
    #if RUN==68
    uint64_t input = 0x5c2cb44e61c5e31;
    #endif
    #if RUN==69
    uint64_t input = 0x7117952db8a5a36d;
    #endif
    #if RUN==70
    uint64_t input = 0xa7c3eae67793368f;
    #endif
    #if RUN==71
    uint64_t input = 0xe32153575cb3aea;
    #endif
    #if RUN==72
    uint64_t input = 0x69f45db72656a20;
    #endif
    #if RUN==73
    uint64_t input = 0xb445c43768363db2;
    #endif
    #if RUN==74
    uint64_t input = 0xd2dee3f7b3d328a;
    #endif
    #if RUN==75
    uint64_t input = 0x83d41141211a3070;
    #endif
    #if RUN==76
    uint64_t input = 0xaeeffbe8b3a29aa;
    #endif
    #if RUN==77
    uint64_t input = 0x37426eb628dc8f;
    #endif
    #if RUN==78
    uint64_t input = 0xd9d1396fb0be37b3;
    #endif
    #if RUN==79
    uint64_t input = 0x448a49f95490baef;
    #endif
    #if RUN==80
    uint64_t input = 0xce58d5af99eb8988;
    #endif
    #if RUN==81
    uint64_t input = 0x308d2aacc7e6d9f0;
    #endif
    #if RUN==82
    uint64_t input = 0x2a99a05013cd369d;
    #endif
    #if RUN==83
    uint64_t input = 0x67ab9da82469378d;
    #endif
    #if RUN==84
    uint64_t input = 0x19f481eec111f53;
    #endif
    #if RUN==85
    uint64_t input = 0xa0b694fc1e7bf73e;
    #endif
    #if RUN==86
    uint64_t input = 0xe3c0b6466c603a22;
    #endif
    #if RUN==87
    uint64_t input = 0xba1dd4b7b963918;
    #endif
    #if RUN==88
    uint64_t input = 0xb7583677839fab;
    #endif
    #if RUN==89
    uint64_t input = 0xfebe218c53c867ef;
    #endif
    #if RUN==90
    uint64_t input = 0xe63b82dbcc55ef;
    #endif
    #if RUN==91
    uint64_t input = 0x53193a187d607afb;
    #endif
    #if RUN==92
    uint64_t input = 0xe2b6a9be5f4732a;
    #endif
    #if RUN==93
    uint64_t input = 0xa0ae5afac2afbbb7;
    #endif
    #if RUN==94
    uint64_t input = 0x142de8db31c9444c;
    #endif
    #if RUN==95
    uint64_t input = 0xdcb2cfa6f42613ff;
    #endif
    #if RUN==96
    uint64_t input = 0x9c6361c818e84a1;
    #endif
    #if RUN==97
    uint64_t input = 0x98e26aeb66448b;
    #endif
    #if RUN==98
    uint64_t input = 0xa041f15461506bf9;
    #endif
    #if RUN==99
    uint64_t input = 0xf1cf67e788e925b;
    #endif
    #if RUN==100
    uint64_t input = 0xee6353e6d77c47;
    #endif
    #if RUN==101
    uint64_t input = 0x23c164f7b8dcf5e1;
    #endif
    #if RUN==102
    uint64_t input = 0x2abc192231768137;
    #endif
    #if RUN==103
    uint64_t input = 0x132eaa5935c9170;
    #endif
    #if RUN==104
    uint64_t input = 0xd7f699602a55a358;
    #endif
    #if RUN==105
    uint64_t input = 0x1978b6a11ce23f;
    #endif
    #if RUN==106
    uint64_t input = 0xf552751e28e297e7;
    #endif
    #if RUN==107
    uint64_t input = 0xb19d8c7c59795876;
    #endif
    #if RUN==108
    uint64_t input = 0x1f8b4a6408cf1c;
    #endif
    #if RUN==109
    uint64_t input = 0x33a42d9b71281d44;
    #endif
    #if RUN==110
    uint64_t input = 0xd7f4826e5d7989;
    #endif
    #if RUN==111
    uint64_t input = 0xa6b93732889bbb61;
    #endif
    #if RUN==112
    uint64_t input = 0x4d9c80df601a19b;
    #endif
    #if RUN==113
    uint64_t input = 0x16efdbd023a4b7f6;
    #endif
    #if RUN==114
    uint64_t input = 0x5be3e9ae5339225e;
    #endif
    #if RUN==115
    uint64_t input = 0x1f2a6175ac2866b;
    #endif
    #if RUN==116
    uint64_t input = 0x8e539242fc6c76d;
    #endif
    #if RUN==117
    uint64_t input = 0xe433f0a1ef9b924;
    #endif
    #if RUN==118
    uint64_t input = 0x153f5c2091f0c5e0;
    #endif
    #if RUN==119
    uint64_t input = 0xae53586c8d3fb643;
    #endif
    #if RUN==120
    uint64_t input = 0x45f6fd7d8b4a85e;
    #endif
    #if RUN==121
    uint64_t input = 0x7dbcfc7fc2dc46;
    #endif
    #if RUN==122
    uint64_t input = 0xb64d2ba7907d3cc6;
    #endif
    #if RUN==123
    uint64_t input = 0x27a74c7d093c04;
    #endif
    #if RUN==124
    uint64_t input = 0x6a1d64cc8ca0aafa;
    #endif
    #if RUN==125
    uint64_t input = 0xfecea6a33d5c2f0;
    #endif
    #if RUN==126
    uint64_t input = 0x92f8d9937e7c309e;
    #endif
    #if RUN==127
    uint64_t input = 0xb045b1a1988753e;
    #endif
    #if RUN==128
    uint64_t input = 0x7705d64262927ec;
    #endif
    #if RUN==129
    uint64_t input = 0xbb617420443ddf57;
    #endif
    #if RUN==130
    uint64_t input = 0x8e198a8a82efc081;
    #endif
    #if RUN==131
    uint64_t input = 0xbea438bfeea747c2;
    #endif
    #if RUN==132
    uint64_t input = 0xceea11dabebb56;
    #endif
    #if RUN==133
    uint64_t input = 0xa0519a4c8d1d69a2;
    #endif
    #if RUN==134
    uint64_t input = 0xc8618e238f21e1b8;
    #endif
    #if RUN==135
    uint64_t input = 0x2732bd97b67ab17;
    #endif
    #if RUN==136
    uint64_t input = 0x8bf609fac2b850;
    #endif
    #if RUN==137
    uint64_t input = 0xfdf3de221a2f4079;
    #endif
    #if RUN==138
    uint64_t input = 0xc472365065c8307c;
    #endif
    #if RUN==139
    uint64_t input = 0xee9710a556bf263c;
    #endif
    #if RUN==140
    uint64_t input = 0xb7fd6347f47f756;
    #endif
    #if RUN==141
    uint64_t input = 0x517192a142b1837;
    #endif
    #if RUN==142
    uint64_t input = 0x2139f10353a7c5a;
    #endif
    #if RUN==143
    uint64_t input = 0x8bfa819c27156c4;
    #endif
    #if RUN==144
    uint64_t input = 0x2a68b4e1b967c5d;
    #endif
    #if RUN==145
    uint64_t input = 0x4c7336cf4c2c86c9;
    #endif
    #if RUN==146
    uint64_t input = 0x432dc2361756e342;
    #endif
    #if RUN==147
    uint64_t input = 0x997ad833414f9a0;
    #endif
    #if RUN==148
    uint64_t input = 0xfed24a4a39219b;
    #endif
    #if RUN==149
    uint64_t input = 0xa6a81e6088e57e8;
    #endif
    #if RUN==150
    uint64_t input = 0x263455e56b3d28;
    #endif
    #if RUN==151
    uint64_t input = 0x939c7a8a4ff6d5e;
    #endif
    #if RUN==152
    uint64_t input = 0xcafe44e11e21ba6;
    #endif
    #if RUN==153
    uint64_t input = 0xce972d542d74d8c;
    #endif
    #if RUN==154
    uint64_t input = 0x3978a85f0f948fa;
    #endif
    #if RUN==155
    uint64_t input = 0x8ec41f57b9572e84;
    #endif
    #if RUN==156
    uint64_t input = 0x1c8fac19f83ae3;
    #endif
    #if RUN==157
    uint64_t input = 0x8cce675b9b2251a4;
    #endif
    #if RUN==158
    uint64_t input = 0x4e145b178b7fd357;
    #endif
    #if RUN==159
    uint64_t input = 0xff5f2c5467759a5b;
    #endif
    #if RUN==160
    uint64_t input = 0x4f27d9bec135d837;
    #endif
    #if RUN==161
    uint64_t input = 0x4142afbe0dd737a;
    #endif
    #if RUN==162
    uint64_t input = 0x9ec3f9ecb9366573;
    #endif
    #if RUN==163
    uint64_t input = 0xf64fec6335bc01b;
    #endif
    #if RUN==164
    uint64_t input = 0x5a7afb70494f1db7;
    #endif
    #if RUN==165
    uint64_t input = 0x4fbd2515b348869;
    #endif
    #if RUN==166
    uint64_t input = 0x4bd6211adcb2c3ab;
    #endif
    #if RUN==167
    uint64_t input = 0xeb2de8e5fa4a7680;
    #endif
    #if RUN==168
    uint64_t input = 0x692e7c51972579;
    #endif
    #if RUN==169
    uint64_t input = 0x3db59e8243d7115f;
    #endif
    #if RUN==170
    uint64_t input = 0x373c9eab1fca6;
    #endif
    #if RUN==171
    uint64_t input = 0x3ac28c64e93089e8;
    #endif
    #if RUN==172
    uint64_t input = 0x37e1d183d39c8625;
    #endif
    #if RUN==173
    uint64_t input = 0x8866e901db4c15;
    #endif
    #if RUN==174
    uint64_t input = 0x5a78b91c9c1d5527;
    #endif
    #if RUN==175
    uint64_t input = 0xb7f179628581eb5;
    #endif
    #if RUN==176
    uint64_t input = 0x8a97c91ae066dd;
    #endif
    #if RUN==177
    uint64_t input = 0x416c4059efb08b18;
    #endif
    #if RUN==178
    uint64_t input = 0x1b711efebec8e716;
    #endif
    #if RUN==179
    uint64_t input = 0x6ebbcfc76bfc89aa;
    #endif
    #if RUN==180
    uint64_t input = 0xdc1885ffbe601859;
    #endif
    #if RUN==181
    uint64_t input = 0xcd3c9e31e3b56;
    #endif
    #if RUN==182
    uint64_t input = 0xf27d6cff1e54bdcb;
    #endif
    #if RUN==183
    uint64_t input = 0x8c6d7a4e7e2a4c9a;
    #endif
    #if RUN==184
    uint64_t input = 0x4eaecb88fd81ff86;
    #endif
    #if RUN==185
    uint64_t input = 0x30ed77babbfc382;
    #endif
    #if RUN==186
    uint64_t input = 0xf116da3ba359c22;
    #endif
    #if RUN==187
    uint64_t input = 0x1faba99fec7c196;
    #endif
    #if RUN==188
    uint64_t input = 0xf12ce973367aa67;
    #endif
    #if RUN==189
    uint64_t input = 0x1434ead6200338;
    #endif
    #if RUN==190
    uint64_t input = 0x44ff54d859fb6a20;
    #endif
    #if RUN==191
    uint64_t input = 0x1b3b70de53780c1;
    #endif
    #if RUN==192
    uint64_t input = 0xc453e5f3928c5b48;
    #endif
    #if RUN==193
    uint64_t input = 0x63e8ee12ce53c9df;
    #endif
    #if RUN==194
    uint64_t input = 0x2b6d3c43b154c4b2;
    #endif
    #if RUN==195
    uint64_t input = 0x28816c315f37c58d;
    #endif
    #if RUN==196
    uint64_t input = 0x12a57876811f1e42;
    #endif
    #if RUN==197
    uint64_t input = 0x4c7bd78232e98b;
    #endif
    #if RUN==198
    uint64_t input = 0x66547cab51f83a89;
    #endif
    #if RUN==199
    uint64_t input = 0xe65ed789552bbe6d;
    #endif
    #if RUN==200
    uint64_t input = 0xa975db1d977aef9;
    #endif
    #if RUN==201
    uint64_t input = 0x8766590eb7c6e;
    #endif
    #if RUN==202
    uint64_t input = 0x2c882ad9e974eefe;
    #endif
    #if RUN==203
    uint64_t input = 0xa6c6c63e33716afc;
    #endif
    #if RUN==204
    uint64_t input = 0xc133311b9c3e7f4a;
    #endif
    #if RUN==205
    uint64_t input = 0xaa36a3758cedf786;
    #endif
    #if RUN==206
    uint64_t input = 0xc77f66ed61de3d5;
    #endif
    #if RUN==207
    uint64_t input = 0xb6ef7c7078496dc;
    #endif
    #if RUN==208
    uint64_t input = 0xd722b1fb1e1347b;
    #endif
    #if RUN==209
    uint64_t input = 0xe1dc95591cda57d9;
    #endif
    #if RUN==210
    uint64_t input = 0x6db37033dc08beb;
    #endif
    #if RUN==211
    uint64_t input = 0xcb4b58e48592d;
    #endif
    #if RUN==212
    uint64_t input = 0x9f70f88ba26e1020;
    #endif
    #if RUN==213
    uint64_t input = 0x56f2b1dd7b2fa91;
    #endif
    #if RUN==214
    uint64_t input = 0x3936f5daf0e7a8d7;
    #endif
    #if RUN==215
    uint64_t input = 0x3e49cfd026cdce21;
    #endif
    #if RUN==216
    uint64_t input = 0x2a1042946f42d97b;
    #endif
    #if RUN==217
    uint64_t input = 0x3cc534de8d5c67a;
    #endif
    #if RUN==218
    uint64_t input = 0x821bcc85163b54b6;
    #endif
    #if RUN==219
    uint64_t input = 0xccca70e8bbb49e66;
    #endif
    #if RUN==220
    uint64_t input = 0xf2734a034ee25e4;
    #endif
    #if RUN==221
    uint64_t input = 0xe131b29dbf337f6;
    #endif
    #if RUN==222
    uint64_t input = 0x57c8ec4576f69c37;
    #endif
    #if RUN==223
    uint64_t input = 0x492df6711f6f39e0;
    #endif
    #if RUN==224
    uint64_t input = 0x80fc5e1e4c33efeb;
    #endif
    #if RUN==225
    uint64_t input = 0xf99a3acca2ff4f50;
    #endif
    #if RUN==226
    uint64_t input = 0xd547358388d15069;
    #endif
    #if RUN==227
    uint64_t input = 0xab4128ee2612cbbb;
    #endif
    #if RUN==228
    uint64_t input = 0x5cbbc981cd52add8;
    #endif
    #if RUN==229
    uint64_t input = 0x13fa6feb1d3e34d;
    #endif
    #if RUN==230
    uint64_t input = 0xa6ba57c5c0799f6;
    #endif
    #if RUN==231
    uint64_t input = 0x2bfa16ef4dada71;
    #endif
    #if RUN==232
    uint64_t input = 0xe4c32ceaeba6a39;
    #endif
    #if RUN==233
    uint64_t input = 0x6a13563f8212c01f;
    #endif
    #if RUN==234
    uint64_t input = 0xbb95eb68d743b379;
    #endif
    #if RUN==235
    uint64_t input = 0x32ce1c7a7fcda6d5;
    #endif
    #if RUN==236
    uint64_t input = 0xbb4688d1b497cca9;
    #endif
    #if RUN==237
    uint64_t input = 0x6b7e195a9414c4c2;
    #endif
    #if RUN==238
    uint64_t input = 0x428363e098efa4b;
    #endif
    #if RUN==239
    uint64_t input = 0xdf994c3963d427;
    #endif
    #if RUN==240
    uint64_t input = 0x3c37b2472b998a1;
    #endif
    #if RUN==241
    uint64_t input = 0xffa7022db2ed2aa;
    #endif
    #if RUN==242
    uint64_t input = 0x11b2f96478b9d785;
    #endif
    #if RUN==243
    uint64_t input = 0x37dc2b04842b51;
    #endif
    #if RUN==244
    uint64_t input = 0xb73fbded2331d;
    #endif
    #if RUN==245
    uint64_t input = 0xb827629d7363ec6e;
    #endif
    #if RUN==246
    uint64_t input = 0xf699c2f78450a532;
    #endif
    #if RUN==247
    uint64_t input = 0xa424856486d8d4;
    #endif
    #if RUN==248
    uint64_t input = 0x849a81979174465e;
    #endif
    #if RUN==249
    uint64_t input = 0x33f34323c1baf71b;
    #endif
    #if RUN==250
    uint64_t input = 0x8a2dba56dd1795;
    #endif
    #if RUN==251
    uint64_t input = 0xb7b62a3ba21c95a;
    #endif
    #if RUN==252
    uint64_t input = 0x216f25881e72dd25;
    #endif
    #if RUN==253
    uint64_t input = 0x833847823d92d738;
    #endif
    #if RUN==254
    uint64_t input = 0xa7e5754186d74732;
    #endif
    #if RUN==255
    uint64_t input = 0x8dfe2ce14962cfe;
    #endif
  #endif
  uint64_t result = input;
  result = des(input, key);
  #if OFFLINE
  printf("Encrypt DES\n");
  printf("Input: %016lx\n", input);
  printf("Des: %016lx\n", result);
  #endif
  return 0;
}
