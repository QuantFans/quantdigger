#ifndef UTIL_CSV

#define UTIL_CSV

#include <iterator>
#include <iostream>
#include <sstream>
#include <vector>
#include <string>
namespace EasyQuant {
using namespace std;
    
class CSVRow
{
 public:
    std::string const& operator[](std::size_t index) const {
        return data_[index];
    }
    std::size_t size() const {
        return data_.size();
    }
    void readNextRow(std::istream& str) {
        std::string         line;
        std::getline(str,line);
        std::stringstream   lineStream(line);
        std::string         cell;
        data_.clear();
        while(std::getline(lineStream,cell,','))
        {
            data_.push_back(cell);
        }
    }
 private:
    std::vector<std::string>    data_;
};

std::istream& operator>>(std::istream& str,CSVRow& data);

class CSVIterator
{   
    public:
        typedef std::input_iterator_tag     iterator_category;
        typedef CSVRow                      value_type;
        typedef std::size_t                 difference_type;
        typedef CSVRow*                     pointer;
        typedef CSVRow&                     reference;

        CSVIterator(std::istream& str)  :str_(str.good()?&str:NULL) { ++(*this); }
        CSVIterator()                   :str_(NULL) {}

        // Pre Increment
        CSVIterator& operator++()               {if (str_) { (*str_) >> row_;str_ = str_->good()?str_:NULL;}return *this;}
        // Post increment
        CSVIterator operator++(int)             {CSVIterator    tmp(*this);++(*this);return tmp;}
        CSVRow const& operator*()   const       {return row_;}
        CSVRow const* operator->()  const       {return &row_;}

        bool operator==(CSVIterator const& rhs) {return ((this == &rhs) || ((this->str_ == NULL) && (rhs.str_ == NULL)));}
        bool operator!=(CSVIterator const& rhs) {return !((*this) == rhs);}
    private:
        std::istream*       str_;
        CSVRow              row_;
};  

} /* EasyQuant */
#endif /* end of include guard: UTIL_CSV */
