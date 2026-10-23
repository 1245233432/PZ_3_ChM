#include "smoothing_spline.hpp"
#include <functional>
#include <iostream>
#include <algorithm>

namespace com_methods {
	smoothing_spline::smoothing_spline(const double& smooth) {
		this->smooth = smooth;
	}

	void smoothing_spline::transition_to_master_element(int seg_num, const double& x, double& ksi) const {
		ksi = 2.0 * (x - points[seg_num].x()) / (points[seg_num + 1].x() - points[seg_num].x()) - 1.0;
	}

	double smoothing_spline::basis_function(int number, const double& ksi) const {
		switch (number) {
		case 1: { return 0.5 * (1.0 - ksi); break; }
		case 2: { return 0.5 * (1.0 + ksi); break; }
		default: { throw std::exception("Error in the basis function number"); break; }
		}
	}

	double smoothing_spline::der_basis_function(int number, const double& ksi) const {
		switch (number) {
		case 1: { return -0.5; break; }
		case 2: { return 0.5; break; }
		default: { throw std::exception("Error in the basis function derivative number"); break; }
		}
	}

	void smoothing_spline::update_spline(const std::vector<Point>& points, const std::vector<double>& F_value) {

		this->points.clear();
		for (auto& elem : points) {
			this->points.push_back(elem);
		}

		int num_segments = points.size() - 1;

		alpha.resize(num_segments + 1); // т.к. dim(OMEGA) = n + 1

		std::vector<double> a, b, c; // диагонали матрицы системы
		a.resize(num_segments + 1); // нижняя побочная диагональ
		b.resize(num_segments + 1); // главная диагональ
		c.resize(num_segments + 1); // верхняя побочная диагональ

		std::function<void(int num_segments, const Point& p, const double& F_val, const double& w)> // процедура для ассемблирования СЛАУ
		Assembling = [&](int i, const Point& p, const double& F_val, const double& w) { // [&] - все определенные выше переменные и функции будут доступны в этом лямбда-выражении
			double x = p.x(), ksi;
			transition_to_master_element(i, x, ksi);
			double f1 = basis_function(1, ksi);
			double f2 = basis_function(2, ksi);
			b[i] += (1.0 - smooth) * w * f1 * f1;
			b[i + 1] += (1.0 - smooth) * w * f2 * f2;
			a[i + 1] += (1.0 - smooth) * w * f1 * f2;
			c[i] += (1.0 - smooth) * w * f2 * f1;

			alpha[i] += (1.0 - smooth) * w * f1 * F_val;
			alpha[i + 1] += (1.0 - smooth) * w * f2 * F_val;
		};

		for (int i = 0; i < num_segments; i++) {
			//double w = 1.0;
			Assembling(i, this->points[i], F_value[i], omega[i]);
			Assembling(i, this->points[i + 1], F_value[i + 1], omega[i + 1]);

			double h = points[i + 1].x() - points[i].x();
			b[i] += 1.0 / h * smooth;
			b[i + 1] += 1.0 / h * smooth;
			a[i + 1] -= 1.0 / h * smooth;
			c[i] -= 1.0 / h * smooth;
		}

		for (int j = 1; j < num_segments + 1; j++) { // метод прогонки, прямой ход
			b[j] -= a[j] / b[j - 1] * c[j - 1];
			alpha[j] -= a[j] / b[j - 1] * alpha[j - 1];
		}

		alpha[num_segments] /= b[num_segments];
		for (int j = num_segments - 1; j >= 0; j--) {
			alpha[j] = (alpha[j] - alpha[j + 1] * c[j]) / b[j];
		}
	}

	void smoothing_spline::get_value(const Point& p, double* res) const {
		double eps = 1e-7;
		int num_segments = points.size() - 1;
		double x = p.x();
		for (int i = 0; i < num_segments; i++) {
			if (x > points[i].x() && x < points[i + 1].x() || fabs(x - points[i].x()) < eps || fabs(x - points[i + 1].x()) < eps) {
				double h = points[i + 1].x() - points[i].x();
				double ksi;
				transition_to_master_element(i, x, ksi);
				res[0] = alpha[i] * basis_function(1, ksi) + alpha[i + 1] * basis_function(2, ksi);
				res[1] = (alpha[i] * der_basis_function(1, ksi) + alpha[i + 1] * der_basis_function(2, ksi)) * 2.0 / h;
				res[2] = 0.0;
				return;
			}
		}
		throw std::exception("The point is not found in the segments");
	}

	void smoothing_spline::set_omega(const std::vector<double>& random_values) {
		omega.clear();
		std::vector<double> sorted_values = random_values; // далее нужен будет исходный вектор
		std::sort(sorted_values.begin(), sorted_values.end()); // сортируем копию вектора выборки

		double q1, q3; // q1, q3 - первый и третий квартили соответсвенно

		double pos1 = 0.25 * (sorted_values.size() - 1);
		double pos3 = 0.75 * (sorted_values.size() - 1); // позиции q1 и q3 в выборке

		size_t low1 = static_cast<int>(pos1);
		size_t high1 = std::min(low1 + 1, sorted_values.size() - 1);
		double fraction1 = pos1 - low1;
		q1 = sorted_values[low1] * (1.0 - fraction1) + sorted_values[high1] * fraction1;

		size_t low3 = static_cast<int>(pos3);
		size_t high3 = std::min(low3 + 1, sorted_values.size() - 1);
		double fraction3 = pos3 - low3;
		q3 = sorted_values[low3] * (1.0 - fraction3) + sorted_values[high3] * fraction3;

		double IQR = q3 - q1; // межквартильный размах

		// определение выбросов
		double LOW = q1 - 1.5 * IQR;
		double HIGH = q3 + 1.5 * IQR;

		for (int i = 0; i < random_values.size(); i++) {
			if (random_values[i] < LOW || random_values[i] > HIGH) {
				omega.push_back(0.3);
			}
			else {
				omega.push_back(1.0);
			}
		}
	}
}