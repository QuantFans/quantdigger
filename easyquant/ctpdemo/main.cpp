#include<iostream>
#include <fstream>
#include <unistd.h>
#include "ctptrader.h"
#include "ctpserver.h"



using namespace std;

//«Î«Û±‡∫≈
int requestId=0;

// «∞÷√µÿ÷∑
//char tradeFront[]="tcp://asp-sim2-front1.financial-trading-platform.com:26205";
//char tradeFront[]="tcp://27.17.62.149:40205";
char tradeFront[]="tcp://27.17.62.149:40213";

void order(const string &line, const CtpTrader& trader) {
    cout<<line<<"*"<<std::endl;
}


int main(int argc, const char *argv[]) {
    using namespace EasyQuant;
//	CtpTrader* pUserSpi = new CtpTrader(tradeFront);
//    pUserSpi->get_user()->Init();
//    ifstream file;
//    string line;
//    while (true) {
//        file.open("test.txt");
//        file>>line;
//        order(line, *pUserSpi);
//        file.close();
//        sleep(1);
//    }
//    pUserSpi->get_user()->Join();
    CtpServer *pserver = new CtpServer(tradeFront);
    pserver->get_user()->Init();
    pserver->get_user()->Join();
//    sleep(3);
//    pUserSpi->ReqQryInstrument("");
//
//pUserApi->Release();
}
