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
	
	int sem_p();
	int sem_v();
private:
	int m_SemId;
};
#endif
