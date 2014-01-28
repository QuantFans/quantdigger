#include "datasource.h" 

int main(int argc, const char *argv[])
{
    EasyQuant::DataSource dd;
    dd.load_order_signal("signal.csv");
    dd.load_history_data("kdata.csv");
    std::cout<<dd.history_data();
    std::cout<<dd.order_signals();
    return 0;
}
