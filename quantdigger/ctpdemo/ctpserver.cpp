#include "ctpserver.h"
#include <iostream>

extern TThostFtdcBrokerIDType appId;		// 应用单元
extern TThostFtdcUserIDType userId;		// 投资者代码


extern int requestId; 

// 会话参数
extern int	 frontId;	//前置编号
extern int	 sessionId;	//会话编号
extern char orderRef[13];

namespace QuantDigger {
using namespace std;
CtpServer::CtpServer(char *tradeFront) {
        user_ = CThostFtdcMdApi::CreateFtdcMdApi();
        user_->RegisterSpi(dynamic_cast<CThostFtdcMdSpi*>(this));			// 注册事件类
        RegisterFront(tradeFront);							// 注册交易前置地址
};




void CtpServer::OnHeartBeatWarning(int nTimeLapse) {
}

void CtpServer::ReqUserLogin(TThostFtdcBrokerIDType	vAppId,
                             TThostFtdcUserIDType	vUserId,	
                             TThostFtdcPasswordType	vPasswd) {
    CThostFtdcReqUserLoginField req;
    memset(&req, 0, sizeof(req));
    strcpy(req.BrokerID, vAppId); strcpy(appId, vAppId); 
    strcpy(req.UserID, vUserId);  strcpy(userId, vUserId); 
    strcpy(req.Password, vPasswd);
    int ret = user_->ReqUserLogin(&req, ++requestId);
    cerr<<" sending | 发送登录..."<<((ret == 0) ? "成功" :"失败") << endl;	
}

void CtpServer::OnRspUserLogin(CThostFtdcRspUserLoginField *pRspUserLogin, 
                               CThostFtdcRspInfoField *pRspInfo, 
                               int nRequestID, 
                               bool bIsLast) {
	if ( !IsErrorRspInfo(pRspInfo) && pRspUserLogin ) {  
    // 保存会话参数	
		frontId = pRspUserLogin->FrontID;
		sessionId = pRspUserLogin->SessionID;
		int nextOrderRef = atoi(pRspUserLogin->MaxOrderRef);
		sprintf(orderRef, "%d", ++nextOrderRef);
       cerr<<" 响应 | 登录成功...当前交易日:"
       <<pRspUserLogin->TradingDay<<endl;     
       // 要接收的合约数据
       char* d[]= { "ru1405" };
        SubscribeMarketData(d, 1);
  }
//  if(bIsLast) sem.sem_v();
}




void CtpServer::OnRspError(CThostFtdcRspInfoField *pRspInfo, 
                           int nRequestID, 
                           bool bIsLast) {
}




bool CtpServer::IsErrorRspInfo(CThostFtdcRspInfoField *pRspInfo) {
	// 如果ErrorID != 0, 说明收到了错误的响应
	bool ret = ((pRspInfo) && (pRspInfo->ErrorID != 0));
  if (ret){
    cerr<<" 响应 | "<<pRspInfo->ErrorMsg<<endl;
  }
	return ret;
}


int CtpServer::ReqUserLogout(CThostFtdcUserLogoutField *pUserLogout, int nRequestID) {
}

void CtpServer::OnRspUserLogout(CThostFtdcUserLogoutField *pUserLogout, 
                                CThostFtdcRspInfoField *pRspInfo, 
                                int nRequestID, 
                                bool bIsLast) {
}

int CtpServer::UnSubscribeMarketData(char *ppInstrumentID[], int nCount) {
}

void CtpServer::OnRspUnSubMarketData(CThostFtdcSpecificInstrumentField *pSpecificInstrument,
                                     CThostFtdcRspInfoField *pRspInfo,
                                     int nRequestID,bool bIsLast) {
}


int CtpServer::SubscribeMarketData(char *ppInstrumentID[], int nCount) {
    if(0 == user_->SubscribeMarketData(ppInstrumentID, nCount))
        cout<<"SubscribeMarketData sucess"<<endl;
    else
        cout<<"SubscribeMarketData error"<<endl;
}

void CtpServer::OnRspSubMarketData(CThostFtdcSpecificInstrumentField *pSpecificInstrument, 
                                   CThostFtdcRspInfoField *pRspInfo, 
                                   int nRequestID, 
                                   bool bIsLast) {
    if (!IsErrorRspInfo(pRspInfo)) {
        cerr<<"响应 | 最新数据！"<<endl;
    } else {
        cerr<<"************"<<endl;
    }
}


void CtpServer::RegisterNameServer(char *pszNsAddress) {
}


void CtpServer::RegisterFront(char *pszFrontAddress) {
    user_->RegisterFront(pszFrontAddress);
    cerr<<"连接交易前置..."<<endl;
}

void CtpServer::OnFrontConnected() {
	cerr<<" 连接交易前置...成功"<<endl;
    ReqUserLogin("1035", "00000071", "123456");
}

void CtpServer::OnFrontDisconnected(int nReason) {
	cerr<<" 响应 | 连接中断..." 
	  << " reason=" << nReason << endl;
}

void CtpServer::OnRtnDepthMarketData(CThostFtdcDepthMarketDataField *pDepthMarketData) {
    cerr<<pDepthMarketData->LastPrice<<endl;
}

} /* QuantDigger */
