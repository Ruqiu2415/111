void qq(int *index,char*arr)
{    int q=index;
    char arr1[10];
    int len=sizeof(arr)/sizeof(arr[0]);
    for(int i=0;i<i<len;i++){
     if (arr[i]>='A'&&arr[i]<='Z'){
         arr1[i]=((arr[i]-'0'-65-q) % 26 + 65)+'0';
        }
    }
   return arr1;
}
void qq(int *index,char*arr)
{    int q=index;
    char arr1[10];
    int len=sizeof(arr)/sizeof(arr[0]);
    for(int i=0;i<i<len;i++){
     if (arr[i]>='0'&&arr[i]<='9'){
         arr1[i]=((arr[i]-'0'-65-q) % 10 + 32)+'0';
        }
    }
   return arr1;
}