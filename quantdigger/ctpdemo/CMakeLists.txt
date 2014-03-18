CMAKE_MINIMUM_REQUIRED(VERSION 2.6 FATAL_ERROR)

FILE(GLOB source
    "*.cpp"
)

ADD_EXECUTABLE (main ${source})
INCLUDE_DIRECTORIES(${CMAKE_SOURCE_DIR})
#LINK_DIRECTORIES("/usr/lib")
TARGET_LINK_LIBRARIES (main
    ${LIBS}/libthostmduserapi.so
    ${LIBS}/libthosttraderapi.so
    )
