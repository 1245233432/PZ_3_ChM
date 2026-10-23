#include <iostream>
#include "cube_spline.hpp"

namespace com_methods {

	void Cube_spline::update_spline(const std::vector<Point>& Points, const std::vector<double>& F_value) {
		this->Points.clear();

		for (auto& elem : Points) {
			this->Points.push_back(elem);
		}

		int num_segment = Points.size() - 1; // общее кол-во сегментов разбиения
		double h_current, h_next; // длины текущего и следующего отрезков

		a.resize(num_segment);
		b.resize(num_segment);
		c.resize(num_segment);
		d.resize(num_segment);

		std::vector<double> f(num_segment - 1); // новый вектор правой части СЛАУ (он на 1 короче, чем num_segment)

		for (int i = 0; i < num_segment - 1; i++) {
			h_current = Points[i + 1].x() - Points[i].x();
			h_next = Points[i + 2].x() - Points[i + 1].x();

			b[i] = 2.0 * (h_current + h_next); // главная диагональ СЛАУ
			a[i + 1] = h_next; // нижняя побочная диагональ
			d[i] = h_next; // верхняя побочная диагональ
			f[i] = 3.0 * ((F_value[i + 2] - F_value[i + 1]) / h_next - (F_value[i + 1] - F_value[i]) / h_current);
		}

		// решение СЛАУ
		for (int j = 1; j < num_segment - 1; j++) { // метод прогонки, прямой ход
			b[j] -= (a[j] / b[j - 1]) * d[j - 1]; // главная диагональ
			f[j] -= (a[j] / b[j - 1]) * f[j - 1]; // вектор правой части
		}

		c[num_segment - 1] = f[num_segment - 2] / b[num_segment - 2]; // последнее c определяется отдельно
		for (int j = num_segment - 2; j > 0; j--) {  // метод прогонки, обратный ход
			c[j] = (f[j - 1] - (d[j - 1] * c[j + 1])) / b[j - 1];
		}
		c[0] = 0.0; // условие нулевой кривизны даёт первое c

		for (int i = 0; i < num_segment - 1; i++) { // на первых n - 1 сегментах
			h_current = Points[i + 1].x() - Points[i].x();
			a[i] = F_value[i];
			b[i] = (F_value[i + 1] - F_value[i]) / h_current - ((2.0 * c[i] + c[i + 1]) / 3.0) * h_current;
			d[i] = (c[i + 1] - c[i]) / h_current / 3.0;
		}

		// на последнем сегменте
		h_current = Points[num_segment].x() - Points[num_segment - 1].x();
		a[num_segment - 1] = F_value[num_segment - 1]; 
		b[num_segment - 1] = (F_value[num_segment] - F_value[num_segment - 1]) / h_current - 2.0 * c[num_segment - 1] * h_current / 3.0;
		d[num_segment - 1] = -c[num_segment - 1] / h_current / 3.0;
	}

	void Cube_spline::get_value(const Point &P, double* Res) const {

		double eps = 1e-7;
		int num_segment = Points.size() - 1;

		for (int i = 0; i < num_segment; i++) {
			if (P.x() > Points[i].x() && P.x() < Points[i + 1].x() || fabs(P.x() - Points[i].x()) < eps || fabs(P.x() - Points[i + 1].x()) < eps) {
				double diff = P.x() - Points[i].x();
				Res[0] = a[i] + b[i] * diff + c[i] * pow(diff, 2) + d[i] * pow(diff, 3);
				Res[1] = b[i] + 2.0 * c[i] * diff + 3.0 * d[i] * pow(diff, 2);
				Res[2] = 2.0 * c[i] + 6.0 * d[i] * diff;
				return;
			}
		}
		throw std::exception("The point is not found in the segments");
	}
}