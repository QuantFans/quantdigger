CMAKE_MINIMUM_REQUIRED(VERSION 2.6 FATAL_ERROR)

FILE(GLOB source
    "*.cpp"
)

ADD_LIBRARY (thirdparty ${source})
INCLUDE_DIRECTORIES(${CMAKE_SOURCE_DIR})
#LINK_DIRECTORIES("/usr/lib")

#TARGET_LINK_LIBRARIES (main
    #${LIBS}/libthostmduserapi.so
    #${LIBS}/libthosttraderapi.so
    #)
INSTALL (FILES 
    ${CMAKE_SOURCE_DIR}/build/util/libutil.a
    #util.py
    DESTINATION "${CMAKE_SOURCE_DIR}/lib/")

