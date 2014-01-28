#include<iostream>
#include "CtpTraderSpi.h"
#include "CSem.h"

using namespace std;

//请求编号
int requestId=0;

// 前置地址
//char tradeFront[]="tcp://asp-sim2-front1.financial-trading-platform.com:26205";
char tradeFront[]="tcp://27.17.62.149:40205";

CSem sem(0);

int main(){
	CThostFtdcTraderApi* pUserApi = CThostFtdcTraderApi::CreateFtdcTraderApi();
	CtpTraderSpi* pUserSpi = new CtpTraderSpi(pUserApi);
	pUserApi->RegisterSpi((CThostFtdcTraderSpi*)pUserSpi);			// 注册事件类
	pUserApi->SubscribePublicTopic(THOST_TERT_RESTART);					// 注册公有流
	pUserApi->SubscribePrivateTopic(THOST_TERT_RESTART);			  // 注册私有流
	pUserApi->RegisterFront(tradeFront);							// 注册交易前置地址
    pUserSpi->ReqQryDepthMarketData("ru1501");
	pUserApi->Init();
	//todo
	
	pUserApi->Join();  
	//pUserApi->Release();
}
