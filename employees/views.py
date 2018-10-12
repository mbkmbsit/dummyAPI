from django.views.generic import View
from django.shortcuts import render, redirect
from django.contrib import messages
import requests
import json
from .forms import searchForm, create_form, update_form


def index(request):
    url = 'http://dummy.restapiexample.com/api/v1/employee/{}'
    url_all = 'http://dummy.restapiexample.com/api/v1/employees'
    all_employees = requests.get(url_all).json()
    results = []
    if request.method == 'POST':
        form = searchForm(request.POST)
        if form.is_valid():
            query = request.POST['search_query'].lower()
            for employee in all_employees:
                for (key, value) in employee.items():
                    if query in value.lower():
                        results.append(employee)
            print("---Search query: "+query)
            print("---Total Results: {}".format(len(results)))
            if results == []:
                messages.warning(
                    request, 'Employee does not exist.  Please try again.')
                form = searchForm()
                url_path = request.path
                return render(request, 'employees/index.html', {'form': form, 'url': url_path})

            employee_id = results[0]['id']
            print("---First Returned Employee: {}".format(employee_id))
            searchedEmployee = requests.get(url.format(employee_id)).json()
    else:
        form = searchForm()
        employee_id = all_employees[0]['id']
        searchedEmployee = requests.get(url.format(employee_id)).json()
        print("---First Employee ID: "+employee_id)
        if searchedEmployee == False:
            messages.warning(
                request, 'Please enter a valid Employee ID:')
            return render(request, 'employees/index.html', {'form': form})
        results.append(searchedEmployee)
    employeeInfo = {
        'id': employee_id,
        'name': searchedEmployee['employee_name'],
        'age': searchedEmployee['employee_age'],
        'salary': searchedEmployee['employee_salary'],
        'image': searchedEmployee['profile_image'],
    }
    url_path = request.path
    context = {'employeeInfo': employeeInfo,
               'form': form, 'results': results, 'url': url_path}
    return render(request, 'employees/index.html', context)


# Trying out Classes instead of Functions (Might not be necessary here, but practice)
class AllEmployees(View):
    url = 'http://dummy.restapiexample.com/api/v1/employees'
    results = requests.get(url).json()

    def get(self, request):
        url_path = request.path
        context = {'url': url_path, 'results': self.results}
        print(f'---Rendered all {len(self.results)} employees by Id (CBV)')
        return render(request, 'employees/index.html', context=context)


class FilteredEmployees(AllEmployees):
    def get(self, request, filter_by):
        url_path = request.path
        results = sorted(
            self.results, key=lambda e: e[f'employee_{filter_by}'])
        context = {'url': url_path, 'results': results}
        print(f'---Rendered all {len(results)} employees by {filter_by} (CBV)')
        return render(request, 'employees/index.html', context=context)

# ----- Original Function-Based allEmployees View -----

# def allEmployees(request):
#     url = 'http://dummy.restapiexample.com/api/v1/employees'
#     results = requests.get(url).json()
#     url_path = request.path
#     context = {'results': results, 'url': url_path}
#     print(f'---Rendered all {len(results)} employees by Id (FBV)')
#     return render(request, 'employees/index.html', context)

# ----- Original Function-Based filteredEmployees View -----

# def filteredEmployees(request, filter_by):
#     url = 'http://dummy.restapiexample.com/api/v1/employees'
#     response = requests.get(url).json()
#     if filter_by == 'name':
#         results = sorted(response, key=lambda e: e["employee_name"])
#     elif filter_by == 'age':
#         results = sorted(response, key=lambda e: e["employee_age"])
#     elif filter_by == 'salary':
#         results = sorted(response, key=lambda e: e["employee_salary"])
#     else:
#         results = response
#     url_path = request.path
#     context = {'results': results, 'url': url_path}
#     print(f'---Rendered all {len(response)} employees by {filter_by} (FBV)')
#     return render(request, 'employees/index.html', context)


def createForm(request):
    url = 'http://dummy.restapiexample.com/api/v1/create'
    if request.method == 'POST':
        form = create_form(request.POST)
        if form.is_valid():
            name = request.POST['name']
            age = request.POST['age']
            salary = request.POST['salary']
            employeeInfo = {'name': name, 'salary': salary, 'age': age}
            data = json.dumps(employeeInfo)
            headers = {
                'Content-Type': 'application/json',
                'Cache-Control': 'no-cache'
            }
            response = requests.request(
                'POST', url, data=data, headers=headers)
            messages.success(
                request, 'You have succesfully added a new user')
            search_url = 'http://dummy.restapiexample.com/api/v1/employee/{}'
            new_id = response.json()['id']
            searchedEmployee = requests.get(search_url.format(new_id)).json()
            employeeInfo = {
                'id': new_id,
                'name': searchedEmployee['employee_name'],
                'age': searchedEmployee['employee_age'],
                'salary': searchedEmployee['employee_salary']
            }
            url_path = request.path
            context = {'employeeInfo': employeeInfo, 'url': url_path}
            print("---Creating new Employee Instance: {}, {} years, ${}".format(
                employeeInfo['name'], employeeInfo['age'], employeeInfo['salary']))
            return render(request, 'employees/index.html', context)

    else:
        url_path = request.path
        form = create_form()
        context = {'url': url_path, 'form': form}
        print('---Initialized employee create form')
        return render(request, 'employees/index.html', context)


def updateForm(request, id):
    url = 'http://dummy.restapiexample.com/api/v1/employee/{}'
    update_url = 'http://dummy.restapiexample.com/api/v1/update/{}'
    searchedEmployee = requests.get(url.format(id)).json()
    if request.method == 'POST':
        form = update_form(request.POST)
        if form.is_valid():
            print("---Updating employee #{}".format(id))
            update_url = update_url.format(id)
            if request.POST['name']:
                name = request.POST['name']
            else:
                name = searchedEmployee['employee_name']
            if request.POST['age']:
                age = request.POST['age']
            else:
                age = searchedEmployee['employee_age']
            if request.POST['salary']:
                salary = request.POST['salary']
            else:
                salary = searchedEmployee['employee_salary']
            employeeInfo = {'name': name, 'salary': salary, 'age': age}
            data = json.dumps(employeeInfo)
            headers = {
                'Content-Type': 'application/json',
                'Cache-Control': 'no-cache'
            }
            requests.request(
                'PUT', update_url, data=data, headers=headers)
            messages.success(
                request, 'You succesfully updated employee #{}'.format(id))
            print("---Employee #{} was successfully updated.".format(id))
    elif requests.get(url.format(id)).json() == False:
        messages.warning(
            request, 'I\'m sorry, that employee does not exist. Please edit an existing employee. ')
        print('Employee #{} does not exist'.format(id))
        return redirect('index')
    searchedEmployee = requests.get(url.format(id)).json()
    employeeInfo = {
        'id': id,
        'name': searchedEmployee['employee_name'],
        'age': searchedEmployee['employee_age'],
        'salary': searchedEmployee['employee_salary']
    }
    form = update_form()
    url_path = request.path
    context = {'employeeInfo': employeeInfo, 'form': form, 'url': url_path}
    return render(request, 'employees/index.html', context)


def deleteEmployee(request, id):
    url = 'http://dummy.restapiexample.com/api/v1/delete/{}'.format(id)
    requests.request('DELETE', url)
    print("---User # {} was successfully deleted".format(id))

    messages.success(
        request, 'You have succesfully deleted employee #{}'.format(id))
    return redirect('index')
