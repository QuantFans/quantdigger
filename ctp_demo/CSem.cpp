#include "CSem.h"

union semun {
int val;   
struct semid_ds  *buf;  
unsigned short *array;
struct seminfo  *__buf;
}sem_union;

CSem::CSem(int value)
{
	m_SemId = semget(IPC_PRIVATE, 1, 0666 | IPC_CREAT);
	if(m_SemId == -1){
		cerr << "error getting sem!" << endl;
	}
	union semun sem_union;
	sem_union.val = value;
	if(-1 == semctl(m_SemId, 0, SETVAL, sem_union)){
		cerr << "error init sem!" << endl;
	}
}

CSem::~CSem()
{
	if(-1 == semctl(m_SemId, 0, IPC_RMID)){
		cerr << "error remove sem!" << endl;
	}
}

int CSem::sem_p()
{
	struct sembuf sbuf;
	sbuf.sem_num = 0;
	sbuf.sem_op = -1;
	sbuf.sem_flg = SEM_UNDO;
	if(semop(m_SemId, &sbuf, 1) == -1){
		cerr<<"semaphore p failed!"<<endl;
		return 0;
	}
	return 1;
}

int CSem::sem_v()
{
	struct sembuf sbuf;
	sbuf.sem_num = 0;
	sbuf.sem_op = 1;
	sbuf.sem_flg = SEM_UNDO;
	if(semop(m_SemId, &sbuf, 1) == -1){
		cerr<<"semaphore v failed!"<<endl;
		return 0;
	}
	return 1;
}
