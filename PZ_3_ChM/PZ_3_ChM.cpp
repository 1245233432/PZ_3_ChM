#include "cube_spline.hpp"
#include "smoothing_spline.hpp"
#include "point.hpp"
#include <iostream>
#include <random>
#include <fstream>
#include <iomanip>
#include <filesystem>

int main() {
	try {
		setlocale(LC_ALL, "rus");
		const int N = 1953; const double M = 1.01; const double s = 3.88;

		std::random_device rd;
		std::mt19937 gen(rd());
		std::normal_distribution<double> d(M, s);

		std::vector<com_methods::Point> mesh; // сетка (аргументы функции)
		std::vector<double> func; // вектор значений функции
		std::vector<double> omega;

		for (int i = 0; i < N; i++) {
			double random_number = d(gen);
			func.push_back(random_number); // ордината y; значение функции - это случайная величина
			mesh.push_back(com_methods::Point(static_cast<double>(i), 0.0, 0.0)); // абсцисса x; аргумент функции - номер наблюдения
			
		}

		const std::vector<double> p_values = { 0.0, 0.4, 0.8, 0.99 };

		std::vector<com_methods::smoothing_spline> smooth_splines;
		smooth_splines.reserve(p_values.size()); //.reserve() резервирует область памяти для этого вектора,
												 // и, в отличие от .resize(), не инициализирует элементы вектора (smooth_splines.size() = 0 после .reserve())
		for (double p : p_values) {
			smooth_splines.emplace_back(p);
			smooth_splines.back().set_omega(func);
			smooth_splines.back().update_spline(mesh, func);
		}

		std::ofstream inFile1("data.csv");
		if (inFile1.is_open()) {
			inFile1 << "n,ksi\n";
			for (int i = 0; i < mesh.size(); i++) {
				inFile1 << mesh[i].x() << ',' << func[i] << '\n';
			}
			inFile1.close();
			std::cout << "Записан data.csv: "<< std::filesystem::absolute("data.csv") << std::endl << std::endl;
		}
		else {
			throw std::runtime_error("Не удалось создать файл data.csv");
		}

		double res[3]; // 0 - значение сплайна в точке, 1 - значение сплайна', 2 - значение сплайна'' (всегда 0)

		std::ofstream inFile2("splines_values.csv");
		if (inFile2.is_open()) {
			inFile2 << std::setprecision(12);
			inFile2 << "x,p=0.0,p=0.4,p=0.8,p=0.99\n";
			for (int i = 0; i < mesh.size(); i++) {
				double x = mesh[i].x();
				inFile2 << x;
				for (const auto& spline : smooth_splines) {
					spline.get_value(mesh[i].x(), res);
					inFile2 << ',' << res[0];
				}
				inFile2 << '\n';
			}
			inFile2.close();
		}
		else {
			throw std::runtime_error("Не удалось создать файл splines_values.csv");
		}
		std::cout << "Записан splines_values.csv: " << std::filesystem::absolute("splines_values.csv") << std::endl << std::endl;

	}
	catch(std::exception &Ex) {
		std::cout << "Error: " << Ex.what() << std::endl;
	}
	return 0;
}