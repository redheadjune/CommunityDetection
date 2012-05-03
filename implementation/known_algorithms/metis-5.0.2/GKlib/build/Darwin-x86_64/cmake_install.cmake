# Install script for directory: /Users/june/Desktop/Communities/CommunityDetection/implementation/known_algorithms/metis-5.0.2/GKlib

# Set the install prefix
IF(NOT DEFINED CMAKE_INSTALL_PREFIX)
  SET(CMAKE_INSTALL_PREFIX "/usr/local")
ENDIF(NOT DEFINED CMAKE_INSTALL_PREFIX)
STRING(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
IF(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  IF(BUILD_TYPE)
    STRING(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  ELSE(BUILD_TYPE)
    SET(CMAKE_INSTALL_CONFIG_NAME "")
  ENDIF(BUILD_TYPE)
  MESSAGE(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
ENDIF(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)

# Set the component getting installed.
IF(NOT CMAKE_INSTALL_COMPONENT)
  IF(COMPONENT)
    MESSAGE(STATUS "Install component: \"${COMPONENT}\"")
    SET(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  ELSE(COMPONENT)
    SET(CMAKE_INSTALL_COMPONENT)
  ENDIF(COMPONENT)
ENDIF(NOT CMAKE_INSTALL_COMPONENT)

IF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Unspecified")
  FILE(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE STATIC_LIBRARY FILES "/Users/june/Desktop/Communities/CommunityDetection/implementation/known_algorithms/metis-5.0.2/GKlib/build/Darwin-x86_64/libGKlib.a")
  IF(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libGKlib.a" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libGKlib.a")
    EXECUTE_PROCESS(COMMAND "/usr/bin/ranlib" "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libGKlib.a")
  ENDIF()
ENDIF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Unspecified")

IF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Unspecified")
  FILE(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include" TYPE FILE FILES
    "/Users/june/Desktop/Communities/CommunityDetection/implementation/known_algorithms/metis-5.0.2/GKlib/gk_arch.h"
    "/Users/june/Desktop/Communities/CommunityDetection/implementation/known_algorithms/metis-5.0.2/GKlib/gk_defs.h"
    "/Users/june/Desktop/Communities/CommunityDetection/implementation/known_algorithms/metis-5.0.2/GKlib/gk_externs.h"
    "/Users/june/Desktop/Communities/CommunityDetection/implementation/known_algorithms/metis-5.0.2/GKlib/gk_getopt.h"
    "/Users/june/Desktop/Communities/CommunityDetection/implementation/known_algorithms/metis-5.0.2/GKlib/gk_macros.h"
    "/Users/june/Desktop/Communities/CommunityDetection/implementation/known_algorithms/metis-5.0.2/GKlib/gk_mkblas.h"
    "/Users/june/Desktop/Communities/CommunityDetection/implementation/known_algorithms/metis-5.0.2/GKlib/gk_mkmemory.h"
    "/Users/june/Desktop/Communities/CommunityDetection/implementation/known_algorithms/metis-5.0.2/GKlib/gk_mkpqueue.h"
    "/Users/june/Desktop/Communities/CommunityDetection/implementation/known_algorithms/metis-5.0.2/GKlib/gk_mkrandom.h"
    "/Users/june/Desktop/Communities/CommunityDetection/implementation/known_algorithms/metis-5.0.2/GKlib/gk_mksort.h"
    "/Users/june/Desktop/Communities/CommunityDetection/implementation/known_algorithms/metis-5.0.2/GKlib/gk_mkutils.h"
    "/Users/june/Desktop/Communities/CommunityDetection/implementation/known_algorithms/metis-5.0.2/GKlib/gk_proto.h"
    "/Users/june/Desktop/Communities/CommunityDetection/implementation/known_algorithms/metis-5.0.2/GKlib/gk_struct.h"
    "/Users/june/Desktop/Communities/CommunityDetection/implementation/known_algorithms/metis-5.0.2/GKlib/gk_types.h"
    "/Users/june/Desktop/Communities/CommunityDetection/implementation/known_algorithms/metis-5.0.2/GKlib/GKlib.h"
    "/Users/june/Desktop/Communities/CommunityDetection/implementation/known_algorithms/metis-5.0.2/GKlib/gkregex.h"
    "/Users/june/Desktop/Communities/CommunityDetection/implementation/known_algorithms/metis-5.0.2/GKlib/ms_inttypes.h"
    "/Users/june/Desktop/Communities/CommunityDetection/implementation/known_algorithms/metis-5.0.2/GKlib/ms_stat.h"
    "/Users/june/Desktop/Communities/CommunityDetection/implementation/known_algorithms/metis-5.0.2/GKlib/ms_stdint.h"
    )
ENDIF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Unspecified")

IF(CMAKE_INSTALL_COMPONENT)
  SET(CMAKE_INSTALL_MANIFEST "install_manifest_${CMAKE_INSTALL_COMPONENT}.txt")
ELSE(CMAKE_INSTALL_COMPONENT)
  SET(CMAKE_INSTALL_MANIFEST "install_manifest.txt")
ENDIF(CMAKE_INSTALL_COMPONENT)

FILE(WRITE "/Users/june/Desktop/Communities/CommunityDetection/implementation/known_algorithms/metis-5.0.2/GKlib/build/Darwin-x86_64/${CMAKE_INSTALL_MANIFEST}" "")
FOREACH(file ${CMAKE_INSTALL_MANIFEST_FILES})
  FILE(APPEND "/Users/june/Desktop/Communities/CommunityDetection/implementation/known_algorithms/metis-5.0.2/GKlib/build/Darwin-x86_64/${CMAKE_INSTALL_MANIFEST}" "${file}\n")
ENDFOREACH(file)
