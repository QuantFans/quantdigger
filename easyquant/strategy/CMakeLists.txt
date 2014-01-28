CMAKE_MINIMUM_REQUIRED(VERSION 2.6 FATAL_ERROR)

FILE(GLOB source
    "*.cpp"
)

ADD_EXECUTABLE (test ${source})
INCLUDE_DIRECTORIES(${CMAKE_SOURCE_DIR})
LINK_DIRECTORIES("${CMAKE_SOURCE_DIR}/build/util")
LINK_DIRECTORIES("${CMAKE_SOURCE_DIR}/build/technical")
LINK_DIRECTORIES("${CMAKE_SOURCE_DIR}/build/engine")

TARGET_LINK_LIBRARIES (test
    util
    technical
    engine
    #${LIBS}/libthosttraderapi.so
    )
