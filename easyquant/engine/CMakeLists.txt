CMAKE_MINIMUM_REQUIRED(VERSION 2.6 FATAL_ERROR)

FILE(GLOB source
    "*.cpp"
)

ADD_LIBRARY (engine ${source})
INCLUDE_DIRECTORIES(${CMAKE_SOURCE_DIR})
LINK_DIRECTORIES("${CMAKE_SOURCE_DIR}/build/util")
LINK_DIRECTORIES("${CMAKE_SOURCE_DIR}/build/technical")

TARGET_LINK_LIBRARIES (engine
    util
    technical
    #${LIBS}/libthosttraderapi.so
    )
