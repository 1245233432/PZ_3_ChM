#pragma once
#ifndef point_h
#define point_h

namespace com_methods {
	class Point {
	private:
		double X, Y, Z;
	public:
		Point(double x = 0, double y = 0, double z = 0);
		double x() const;
		double y() const;
		double z() const; // геттеры координат точки
	};
}

#endif