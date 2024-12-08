%{
% Load the .mat file
loaded_data = load('no_manip_data.mat');

% Access the 3D array from the loaded data (this should be your 30x150x4 array)
data_array = loaded_data.cell_array;

% Access the 1st matrix (this is the 1st slice of the 3D array)
matrix_1 = squeeze(data_array(1, :, :));  % Extract the 1st matrix

% Display the 1st matrix
disp('Matrix 1:');
disp(matrix_1);
%}
% Load the .mat file
loaded_data = load('AF_manip_data.mat');

% Access the 3D array from the loaded data
data_array = loaded_data.cell_array; % Assuming the 35x150x4 data is stored in 'cell_array'

% Initialize arrays to store sensor data
num_sensors = size(data_array, 3); % Number of sensors (columns in each matrix)
num_matrices = size(data_array, 1); % Number of matrices (35 in this case)
sensor_data = zeros(num_matrices, num_sensors);

% Extract the first row of each matrix for each sensor
for i = 1:num_matrices
    for sensor = 1:num_sensors
        sensor_data(i, sensor) = data_array(i, 1, sensor); % First row of matrix, column = sensor
    end
end

% Plot each sensor's data
figure;
for sensor = 1:num_sensors
    subplot(num_sensors, 1, sensor); % Create a subplot for each sensor
    plot(sensor_data(:, sensor), 'o-', 'LineWidth', 1.5); % Plot data for the sensor
    title(['Sensor ', num2str(sensor)]);
    xlabel('Matrix Index');
    ylabel('Sensor Value');
    grid on;
end

