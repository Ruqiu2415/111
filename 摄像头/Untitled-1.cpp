#include<stdio.h>   
#include <string.h>
#include <ctype.h>

int main() {
    char str[] = "ewii223jj11,01da";
    char num, num1;

    number(str, &num, &num1);

    printf("num: %c\n", num);   // 输出个位数字
    printf("num1: %c\n", num1); // 输出十位数字

    return 0;
}
void number(char *str, char *num, char *num1) {
    char arr[10] = {0};
    char arr1[10] = {0};
    int Num = 0;
    int Num1 = 0;
    int len = strlen(str);

    for (int i = 0; i < 2; i++) {
        int q = 0;
        for (int j = q; j < len; j++) {
            if (isdigit(str[j]) && i == 0 && str[j] != '0') {
                arr[Num] = str[j];
                Num++;
            } else if (isdigit(str[j]) && i == 1) {
                arr1[Num1] = str[j];
                Num1++;
            } else {
                q = j + 1;
                break;
            }
        }
    }
    int Q = 0;
    int Q1 = 0;
    int a = strlen(arr);
    int b = strlen(arr1);

    for (int i = 0; i < a; i++) {
        Q = Q * 10 + (arr[i] - '0');
    }
    for (int i = 0; i < b; i++) {
        Q1 = Q1 * 10 + (arr1[i] - '0');
    }
    Q = Q + Q1;
    *num = Q % 10 + '0';
    *num1 = ((Q - '0') % 10) + '0';
}
