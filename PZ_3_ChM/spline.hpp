#pragma once
#ifndef spline_h
#define spline_h

#include <vector>
#include "point.hpp"

namespace com_methods {
	class Spline { // произвольный сплайн
	public:
		// сетка и соответствующие значения табличной функции
		virtual void update_spline(const std::vector<Point>& Points, const std::vector<double>& F_value) = 0;
		// точка, в которой вычисляется значение и массив для хранения полученного значения сплайна и его производных
		virtual void get_value(const Point& P, double* res) const = 0;
	};
}

#endif 