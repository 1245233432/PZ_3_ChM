# CMakeList.txt: проект CMake для PZ_3_ChM; включите исходный код и определения,
# укажите здесь логику для конкретного проекта.
#

# Добавьте источник в исполняемый файл этого проекта.
add_executable (PZ_3_ChM "PZ_3_ChM.cpp" "smoothing_spline.cpp" "point.cpp")

if (CMAKE_VERSION VERSION_GREATER 3.12)
  set_property(TARGET PZ_3_ChM PROPERTY CXX_STANDARD 20)
endif()