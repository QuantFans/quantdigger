#ifndef CSEM_H
#define CSEM_H
#include<iostream>
#include<sys/ipc.h>
#include<sys/types.h>
#include<sys/sem.h>

using namespace std;

class CSem{
public:
	CSem(int);
	~CSem();
	
    //! 获取资源
	int sem_p();
    //! 释放资源
	int sem_v();
private:
	int m_SemId;
};
#endif
