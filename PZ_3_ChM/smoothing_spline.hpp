#pragma once
#ifndef smoothing_spline_h
#define smoothing_spline_h

#include "spline.hpp"

namespace com_methods {
	class smoothing_spline : public Spline {
	private: 
		double smooth;	           // параметр сглаживания p
		std::vector<Point> points; // точки сетки
		std::vector<double> alpha; // коэффициенты разложения по базису alpha(i)
		std::vector<double> omega; // весовые коэффициенты
		void transition_to_master_element(int seg_num, const double& x, double& ksi) const; // переход на мастер-элемент [-1, 1], num_seg - номер сегмента, 
																							// x - абсцисса
																							// ksi - координата (замена переменной)
		double basis_function(int number, const double& ksi) const; // базисные функции на отрезке [-1, 1], number - номер функции, ksi - координата на мастер-элементе
		double der_basis_function(int number, const double& ksi) const; // производные базисных функций
	public:
		smoothing_spline(const double& smooth); // конструктор сплайна
		void update_spline(const std::vector<Point>& points, const std::vector<double>& F_value) override; // обновление сплайна для новой сетки
		void get_value(const Point& p, double* res) const override;
		void set_omega(const std::vector<double>& random_values);
	};
}

#endif