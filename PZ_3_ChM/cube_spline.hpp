#pragma once
#ifndef cube_spline_h
#define cube_spline_h

#include "spline.hpp"

namespace com_methods {
	class Cube_spline : public Spline {
	private:
		std::vector<Point> Points;
		std::vector<double> a, b, c, d;
	public:
		void update_spline(const std::vector<Point>& Points, const std::vector<double>& F_value) override;
		void get_value(const Point& P, double* res) const override;
	};
}

#endif