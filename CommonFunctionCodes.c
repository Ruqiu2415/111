/*小创播报*/
YY_Text(char text[])        /*语音播报字母数字*/
YY_CP(char text[])			/*语音播报车牌*/
YY_Time(uint8_t ali_year, uint8_t ali_month, uint8_t ali_day, uint8_t ali_hour, uint8_t ali_minute, uint8_t ali_second)/*语音播报时间*/
fh(int num)					/*语言播报十百千*/
YY_weather(uint8_t weather) /*语言播报天气*/
YY_temperature(uint8_t temperature)/*语言播报温度(十进制)*/
YY_CJ(uint16_t dis, uint8_t dw)/*语言播报距离*/
TTS(char* text);				/*语言播报(可播报中文)*/
YY_BZW(uint8_t mainOrder, uint8_t num)//好东西//对应词条使用



Uploading(uint8_t num)				//上传评分系统
											


/*小车行动*/
Car_Go(uint8_t speed, uint16_t distance);		/*前进*/
Car_Back(uint8_t speed, uint16_t distance);		/*后退*/
ali_back(int numOrletter, int isLandmark);		//倒车入库numOrletter:数字库为1，字母库随便  isLandmark：有标志物就填1
Back_Garage_2(uint8_t choice);					/*倒车入库车库前面有标志物*/
Back_Garage_3(uint8_t choice);					//车库前面有地形
Out_Garage_2(uint8_t choice);					//码盘出库
Reverse_exit();									 //倒车出库
Double_Dodge();									//打开双闪
Double_Flash_off();								//双闪关闭
left(uint8_t model);							//左转
right(uint8_t model);							//右转
highSpeed(80);									//高速循迹
videoLineMP(uint8_t spend, int distance);		//码盘循迹
Video_Line_4(uint8_t spend, uint8_t len);		//过地形len：1为短道 2为长道
headNew_Trixutixi(1);							//过地形 1为长道 2为短道
headNew();										//车头摆正
headAMD();										//车头摆正
head();											//车头摆正

//自己写的车头摆正




/*摄像头功能*/
initPhotosensitive(1);					/*摄像头初始化*/
servoControl(int8_t angle);				/*舵机角度控制函数*/
Identify_QR_2(uint8_t sheet, uint8_t size, uint8_t around);/*识别二维码*/
identifyTraffic(1);						//识别交通灯
rangingQR(uint8_t sheet, uint8_t size, uint8_t around)//测距二维码
rangingcolourQR(uint8_t sheet, uint8_t size, uint8_t around);//测距彩色二维码
Identify_colourQR_2(uint8_t sheet, uint8_t size, uint8_t around);//识别彩色二维码


 /*道闸*/
Gate_Open_Zigbee(uint8_t number);		// 道闸闸门开启
Gate_Show_Zigbee(char* Licence, uint8_t number)		// 道闸系统标志物显示车牌


/*LED*/
LED_Data_Zigbee(uint8_t One, uint8_t Two, uint8_t Three, uint8_t rank);			/*LED显示标志物显示数据	 参数：16进制	rank-行数*/
LED_Data2_Zigbee(uint8_t* data, uint8_t rank, uint8_t toHEX, uint8_t number);	// LED显示标志物显示数据2传参为ascll
LED_Dis_Zigbee(uint16_t dis, uint8_t choice, uint8_t number);					//LED显示超声波距离
LED_time_Zigbee(uint8_t choice, uint8_t number);								// LED显示标志物计时状态



/*TFT*/
TFT_Test_Zigbee(char Device, uint8_t Pri, uint8_t Sec1, uint8_t Sec2, uint8_t Sec3，number);/*TFT显示标志物控制指令*/
TFT_Dis_Zigbee(char Device, uint16_t dis, number);								/*智能TFT显示器显示距离信息*/
TFT_Show_Zigbee(char Device, char* Licence,number);										/*TFT显示器显示车牌*/
TFT_WhichPic_Zigbee(char Device, uint8_t which, uint8_t number);					//显示指定页数图片
TFT_show_Hex2(char Device, uint8_t one, uint8_t two, uint8_t three, uint8_t number);//指定TFT显示HEX模式
TFT_Sign_Zigbee(char Device, uint8_t which, uint8_t number);						//指定TFT显示交通标志
LicensePlate_Pattern_recognition(uint8_t module);									/*TFT执行翻页操作*/
TFT_Hex_Zigbee(char Device, char* Licence, uint8_t transition, uint8_t number)		//TFT显示器显示hex数据   transition 是否为数字 是数字填0，字符填1

/*公交站*/
YY_Comm_Zigbee(uint8_t Primary, uint8_t Secondary)				//控制语音播报标志物播报语音控制命令
Bus_Dat_Control_Data(uint8_t year, uint8_t month, uint8_t day, uint8_t number);//设置公交车站年月日
Bus_Dat_Inquire_Data(uint8_t number);								//查询公交车站日期
Bus_Time_Control_Data(uint8_t hour, uint8_t minute, uint8_t second, uint8_t number);//设置公交车站时分秒
CX_Bus_Time_Inquire_Data(uint8_t number)
Bus_Dat_Weather_Data(uint8_t weather, uint8_t temp, uint8_t number);//设置公交车站天气温度
Bus_Dat_InquireTQ_Data(uint8_t number);							//查询公交车站天气

YYSB(void)					//// 语音播报随机指令
YY_Play_Zigbee_2(uint8_t* p);								//播报指定文本
YY_Play_Zigbee(uint8_t* s_data);						   //不可播报中文
/*路灯*/
Light_Inf_1(uint8_t gear);											/*自动调节光照强度函数*/



/*随机路线*/
getLX(uint8_t* LX, const char* data);						/*取出随机路线的数据*/
openRandomPath(uint8_t* dw, char cfx, 20);							//随机路线	（路线，车头初始方向，20）数字越小为北
setRW(uint8_t zb, char rwdh, char rwfx, char ifxh);          /*设置任务点：zb：任务点的坐标     rwdh:任务详情(sendTask();中)     rwfx:任务方向:任务方向     ifxh：是否销毁标志位	1:保留	0：销毁*/

/*红外线发数据*/
Infrared_Send_degree(uint8_t* s, uint8_t number, uint16_t ms);/*红外发送控制次数默认红外数据为6位*/


/*无线电*/
Wireless_Charging_KEY(uint8_t* Charge_buf, uint8_t number);				/*开启码开启无线电*/
Wireless_Charging_KEY2(uint8_t buf_1, uint8_t buf_2, uint8_t buf_3, uint8_t buf_4, uint8_t number);/*开启码开启无线电*/
Wireless_Charging_Close(uint8_t number);									/*开启码开启无线电*/


/*立体显示*/
Rotate_show_Inf_2(uint8_t* src, char x, char y, uint8_t number);		// 立体显示标志物显示车牌数据
Rotate_show_Inf_dis_size(uint16_t num);									//立体显示测距
dis_sizeShow(int value, char dw, char x);										//立体显示显示距离
Rotate_FontColor_Inf_2(uint8_t colour, uint8_t number);					//设置文本颜色
Rotate_Empty(uint8_t Sec1, uint8_t number);								//立体显示清空自定义文本
Rotate_show_Text(char* text, uint8_t ifZigBee);							//立体显示自定义文本
Rotate_show_Text2(char* text, uint8_t ifZigBee);						//累计自定义（最后需要用Rotate_show_Text(char* text, uint8_t ifZigBee);	显示）

/*车库*/
Garage_Cont_Zigbee(char Device, uint8_t Floor);							//立体车库到达指定车库(运行并等待)
Garage_GetFloor_Zigbee(char Device);									//获取指定车库层数
Garage_AB_Zigbee(uint8_t A_Floor, uint8_t B_Floor);						//A、B车库到达指定层数(运行并等待)
Garage_convenien_Zigbee(char Device, uint8_t Floor);					//指定车库到达指定层数(不可出库)





/*烽火台*/
single_point_beacon(uint8_t* beacon_buf);								/* 扫射激活烽火台 */
single_Location();														//请求回传烽火台坐标


/*蜂鸣器*/
Tba_BEEP(uint16_t HT, uint16_t LT, uint16_t number);					//任务板蜂鸣器
Cba_Beep(uint16_t HT, uint16_t LT, uint16_t number);					//核心板蜂鸣器


/* 超声波 */
void UltrasonicRanging_Model(uint8_t model, uint8_t choice, uint8_t wheel);

Car_Track(AGV_GO_sp);          /*无限码盘循迹前进*/
Amendment_Front_AXLT();         /*车头摆正*/

/*延时*/ delay_ms(uint16_t ms);										


/*############################################################################################################################################################################################################################*/

//循迹板循迹                                                             
TGO();      /*循迹到下一个路口   */                        servoControl(-60);			/*摄像头角度*/			openRandomPath(uint8_t* dw, char cfx, 12);//'随机路线
TGO_1();   /*长道循迹*/                                    initPhotosensitive(1);		/*摄像头初始化*/		setRW(uint8_t zb, char rwdh, char rwfx, char ifxh);//随机路线设置任务
TGO_2();   /*短道循迹*/                                    videoLine(40);				/*循迹到路口*/			printArr(uint8_t* arr);		//打印数组
Car_Go(AGV_GO_sp, AGV_GO_mp);  /*码盘不循迹*/   	       videoBlackLine(40);			/*循迹到黑线*/			printHexArr(uint8_t* arr);	//打印十六进制数组
Car_Back(50, 420);             /*码盘后退*/				   videoLineMP(80, 2200);			/*码盘循迹*/			Serial.println("");			//打印字符串
MP(40, 800);					/*码盘循迹*/				highSpeed(80);				/*高速巡航*/
Car_BackBlackLine(25, 500);    /*后退到黑线*/			   Video_Line_4(80);			/*能过随机地形*/
Car_Track(AGV_GO_sp);          /*无限码盘循迹前进*/		   videoLineTerrain(40, 0);	    /*循迹到十字路口能过地形*/
Car_TrackMP(55, 800);           /*码盘循迹前进*/		   VideoLineDis(20);			/*慢速循迹*/
VideoLineBreak(70);
headAMD();					/*车头修正*/
VideoLineBreak(70);//后退到黑线
Car_RorL(uint8_t LorR, uint8_t sp, uint16_t angle);//转弯任意码盘

Car_RorL(1, 90, LM);		/*码盘左转*/					Send_InfoData_To_Fifo(uint8_t* data_Array, uint8_t len);	/*打印数组*/
Car_RorL(1, AGV_wheel_sp, LMB);	   /*速度码盘左转*/			Serial.println("");											/*打印字符串并换行*/
Car_RorL(2, 100, RM);	           /*码盘右转*/				Serial.print("");											/*打印不换行*/
Car_RorL(2, AGV_wheel_sp, RMB);	   /*速度码盘右转*/			ZeroAry(shijian, 20);										/*数组清零*/
Car_RorL(2, AGV_wheel_sp, 430);								peintln_u8s(uint8_t* text);/*打印数组*/

//从车计算机视觉部分											//地形（摄像头）			//小创
identifyTraffic(1);			/*交通灯*/							Video_Line_4(80, 1); 		YY_Text("ABC123");//小创播报字母数字
Identify_QR_2(2, 0, 2);		/*识别二维码	数量 大小 姿态*/								YY_CP("B123C4");//小创播报车牌
rangingQR(2, 0, 2);			/*测距二维码*/													YY_Num_Hex(0x16);//十六进制直接播报(0x16播报为十六)
YY_weather(1);/*小创播报天气*/																YY_aNum(uint16_t num);//逐个播报数字
/*车头摆正(循迹板)*/																		YY_Num(23);//小创播报数字(十六进制自动会转换)
		
		Back_ruku(choice);		/*到车入库*/
		Back_Garage(choice);    /*到车入库*/


Amendment_Front_AXLT();         /*车头摆正*/		Back_Garage_2(choice);  /*到车入库*/
Back_Garage_3(choice);	/*到车入库*/				ali_back(int numOrletter, int isLandmark); // numOrletter:数字库为1，字母库随便  isLandmark：有标志物就填1
Back_Garage_4(choice);  /*到车入库*/
leftOrRightAdjust(uint8_t LOrR);	/*侧身摆正*/
/*出库*/
Out_Garage();		     /*出库*/								//测距
Out_Garage_2(1);          /*出库*/								UltrasonicRanging_Model(3, 1, 0);    /*测距 */
Reverse_exit();          /*倒车出库*/							UltrasonicRanging_Model_2();		/*后退到黑线测距*/
VideoLineCentreAdjust();			/*中心点摆正*/
//无线电
Wireless_Charging(3);											/*默认激活码开启无线电*/
Wireless_Charging_KEY(Charge_buf, 3);							/*数组开启无线电*/
Wireless_Charging_KEY2(buf_1, buf_2, buf_3, buf_4, number);		/*单个字符开启无线电*/
Wireless_Charging_Close(3);										/*默认激活码关闭*/

/*路灯*/														/*道闸*/
Light_Inf(gear);			/*调灯(返回u8初始档位)	*/			Gate_Open_Zigbee(2);		  //默认开启码开启到闸
Light_Inf_1(gear);			/*调灯(返回u8初始档位)	*/			Gate_Show_Zigbee(ali_cp, 2); //车牌开启道闸
light_add(gear);	       /*调灯(返回u8初始档位)	*/

/*烽火台*/														/*LED*/
single_point_beacon(Beacon_Tower);		/*单点激活烽火台*/		LED_Data_Zigbee(One, Two, Three, rank);/*LED显示数据*/
Car_RorL_Alarm(infrare_com, 1);         /*左转激活烽火台*/		LED_Data2_Zigbee(Data, rank, toHEX, 2);/*ED显示数据自动转HEX*/
Car_RorL_Alarm(infrare_com, 2);         /*右转激活烽火台*/		LED_Dis_Zigbee(dis_size, choice, 2);	/*LED第二排显示距离*/
single(infrare_com_buf, infrare_com);    /*双数据激活烽火台*/   LED_time_Zigbee(choice, 2);				/*LED时间 0：清零 1：开启 2：关闭*/
single_point_beacon_2(infrare_com);       /*扫射激活烽火台*/
single_point(Beacon_Tower);               /*扫射激活烽火台*/			//蜂鸣器
single_Location();                      /*扫射激活烽火台*/				Cba_Beep(50, 50, 3);/*核心板蜂鸣器*/
Smoke_Towers(infrare_com, 3);            /*扫射激活烽火台*/				Tba_BEEP(50, 50, 3);/*任务板蜂鸣器*/
headNew_Trixutixi( int len) //新的过特殊地形前进
/*地形(循迹板)*/														/*TFT*/
Judge_terrain();   /*过地形, 无论是有地形还是没有地形都照样过*/			TFT_Test_Zigbee('A', Pri, Sec1, Sec2, Sec3, number);  /*TFT显示信息*/
Fixed_Terrain();														TFT_Sign_Zigbee('A', 1, 3);				/*TFT显示交通标志 01直行 02左转 03右转 04掉头 05 禁止直行 06 禁止通行*/
Fixed_Terrain_2();   													TFT_Dis_Zigbee('A', dis_size, 3);					 /*TFT显示距离*/
Fixed();																TFT_Disdate_Zigbee('A', date_1, date_2, 3);			 /*TFT显示距离*/
Fixed_Terrain_3();  /*码盘过长地形*/									TFT_Show_Zigbee('A', GateStr, 3);					/*TFT显示车牌*/
Fixed_Terrain_4(); /*码盘过短地形*/										TFT_Hex_Zigbee('A', GateStr, 1, 3);					/*TFT显示HEX模式 例如"A1B2C3"*/
Random_Terrain();														TFT_WhichPic_Zigbee('A', 1, 3);						/*TFT显示指定页数的图片*/
Judge_terrain_2();														TFT_show_Hex2('A', one, two, three, 3);				/*TFT显示HEX模式 例如"A1B2C3"*/
Terrain_And_Card_AXLT();												LicensePlate_Pattern_recognition(uint8_t model);   /*TFT直行翻页操作*/
Terrain_And_Card_Offset_easy();
Terrain_And_Card_Offset_difficul();
TerrainBack_Zigbee(number);														/*公交车站*/
YY_Play_Zigbee(uint8_t* s_data);			 /*语音标志物播报数据*/				YY_Comm_Zigbee(0x10, Secondary);			  /*控制语音播报标志物播报语音控制命令*/
/*立体车库*/																	YYSB();										/*小创语音识别公交站*/
Garage_Test_Zigbee('A', 0x01, 0x01, 3);  /*主指令复指令控制车库*/				Bus_Dat_Control_Data(0x21, 0x11, 0x05, 2);    /*公交站台显示年月日*/
Garage_Cont_Zigbee('A', 1);				/*车库A到达指定层数（可入库出库）*/		Bus_Time_Control_Data(0x11, 0x12, 0x13, 2);   /*公交站台显示时分秒*/
Garage_Cont_Zigbee('B', 1);	            /*车库B到达指定层数（可入库出库）*/	
Garage_GetFloor_Zigbee('A');			 /*获取车库层数*/						Voice_broadcast_digital(num);               /*语音播报数字*/
Garage_convenien_Zigbee('A', 1);		/*车库到达指定层数(不可出库！！！)*/	Bus_Dat_InquireTQ_Data(3);                 /*获取天气*/
Garage_AB_Zigbee(A_Floor, B_Floor);     /*降两个车库*/							Bus_Dat_Weather_Data(0x00, 0x19, 3);       /*设置天气*/

/*立体显示*/
Rotate_show_Inf_2((char*)GateStr, RFID_Position[0], RFID_Position[1], 3);   /*立体显示显示车牌*/
Rotate_Dis_Inf(dis_size, 2);											    /*立体显示显示距离*/
Rotate_Disdata_Inf(data_1, data_2, number);									/*立体显示显示距离*/
Rotate_roadCondition_Inf(choice, 3);										/*立体显示显示路况信息*/
Rotate_Colour(data, number);												/*立体显示显示颜色0x01:红/0x02:绿/0X03:蓝/0x04:黄/0x05:品色/0x06:青/0x07:黑/0x08:白*/
Rotate_FontColor_Inf_2(uint8_t colour, 3);									/*设置立体显示字体颜色0x01:红/0x02:绿/0X03:蓝/0x04:黄/0x05:品色/0x06:青/0x07:黑/0x08:白*/
Rotate_Shape(shape, number);		    									/*立体显示形状0x01:矩形	/0x02:圆形 /0x03:三角形 /0x04:菱形 /0x05:五角星*/
Rotate_Sign_Inf(sign_date, number);											/*立体显示交通标志0x01 直行/0x02 左转 /0x03 右转/0x04 掉头/0x05 禁止直行 /0x06 禁止通行*/
Rotate_Empty(0x02, 3);														/*立体显示清空自定义文本*/
Rotate_show_Inf_Bus(uint8_t num)；											/*立体显示车站信息*/
Rotate_show_Text(char* text, uint8_t ifZigBee);								//立体显示自定义文本

Rotate_Text(uint8_t* Sec1, 1, uint8_t select);										/*立体显示字符zigbee 只能发一个字*/
Rotate_Text2((uint8_t Sec1, uint8_t Sec2, uint8_t number, uint8_t select));			/*立体显示字符zigbee 只能发一个字*/
Rotate_Infrared_Text(uint8_t* Sec1, 1, uint8_t select);								/*立体显示自定义文本红外 只能发一个字*/
Rotate_Infrared_Text2(uint8_t Sec1, uint8_t Sec2, uint8_t number, uint8_t select);	/*立体显示自定义文本红外 只能发一个字*/
Rotate_Infrared_u8long(const uint8_t* Sec1, uint8_t number);						/*红外自定义长文本（阿斯科码）*/
//Rotate_ZigBeeText_u8long(const uint8_t* Sec1);										/*ZigBee自定义长文本（阿斯科码）*/
Rotate_show_Text(char* src, uint8_t ch);											/*立体显示自定义长文本  ch==1 ZigBee  ch==2:红外 */

/*转向灯*/										/*获取循迹灯*/
LED.LeftTurnOn();  /*左转向灯开启*/				H8_HEX(void);       //H8_HEX() == 0xFF;
LED.RightTurnOn(); /*右转向灯开启*/				Q7_HEX(void);
LED.LeftTurnOff(); /*左转向灯关闭*/				Tracking_light_Count(uint8_t gd, uint8_t ogd);
LED.RightTurnOff();/*右转向灯关闭*/
Double_Dodge();	/*双闪灯打开*/
Double_Flash_off();	/*双闪灯关闭*/

/*功能代码*/
Colon_sort((char*)temp_array, 1);						//排序      0表示从小到大  1表示从大到小	         
Bubble_Sort_To_N_L(u8* Data, int Big_Small, int N_L);		//冒泡排序
getNum_A(char* tempArrays, const int num);				//将一个数字拆解成数组
Reverse((char*)READ_RFID);									//将字符串倒序
take_out_AoutHex(char* letters);							//将char类型的A转为0x0A(大于F的就会转换成对应的十六进制数字，G=>0x10)
copy(char* arr, const char* tempArray);			//复制一个数组
int calculator(char* string);								//计算器 支持括号、幂运算、sin、cos、tan、asin、acos

/**************************************** 部分常用参数 *****************************************************/
/*
车牌：ali_cp[6]						年：ali_year			月：ali_month				日：ali_day
最终车库层数：ali_ckcs				时：ali_hour			分：ali_minute				秒：ali_second
地形状态：ali_dx					语音播报：ali_yybb		烽火台激活码：ali_fht[6]	TFT数据：ali_tft[6]
路灯初始档位：ali_ldC				路灯最终档位：ali_ldZ	地形位置：ali_dx			主车识别到的公交车站：ali_gjz
交通灯(A)：trafficLightA_Color		交通灯(B)：trafficLightB_Color						立体显示数据：ali_ltxs[12]
无线电激活码：ali_wxd[4]			天气：ali_tq			温度：ali_wd				测距：	ali_dis_size
车库初始层数(A)：GarageA_Floor		车库初始层数(B)：GarageB_Floor
*/