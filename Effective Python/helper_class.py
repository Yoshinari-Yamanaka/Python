# -*- encoding:utf-8 -*-
import json

def json_serialize(obj):
    if isinstance(obj,tuple):
        return list(obj)
    return obj

class Subject(object):
    __slots__ = ["_grades"]

    def __init__(self):
        self._grades = []

    def report_grade(self, score, weight):
        self._grades.append((score, weight))

    def average_grade(self):
        total, total_weight = 0, 0

        for grade in self._grades:
            total += grade[0] * grade[1]
            total_weight += grade[1]

        return total / total_weight

    def get_score(self):
        if len(self._grades) == 0:
            return self._grades
        
        grades = []
        for name in self._grades:
            grades.extend(self._grades.copy())
        return grades

class Student(object):
    __slots__ = ["_subjects"]

    def __init__(self):
        self._subjects = {}

    def subject(self, name):
        if name not in self._subjects:
            self._subjects[name] = Subject()
        return self._subjects[name]

    def average_grade(self):
        total, count = 0, 0
        for subject in self._subjects.values():
            total += subject.average_grade()
            count += 1

        return total / count
    
    def get_student(self):
        if len(self._subjects) == 0:
            return self._subjects
        
        student = {}
        for name in self._subjects:
            student[name] = self._subjects[name].get_score()
        return student

class Gradebook(object):
    __slots__ = ["_students"]

    def __init__(self):
        self._students = {}

    def student(self, name):
        if name not in self._students:
            self._students[name] = Student()

        return self._students[name]
    
    def get_book(self):
        if len(self._students) == 0:
            return self._students
        
        book = {}
        for name in self._students:
            book[name] = self._students[name].get_student()
            yield book

def main():
    # Student Linus
    book = Gradebook()
    student = book.student("Linus")
    math = student.subject("Math")
    math.report_grade(20,0.3)
    science = student.subject("Science")
    science.report_grade(40,0.6)
    print(student.average_grade())

    # Student Bill
    albert = book.student("Bill")
    math = albert.subject('Math')
    math.report_grade(80, 0.10)
    math.report_grade(80, 0.10)
    math.report_grade(70, 0.80)
    gym = albert.subject('Gym')
    gym.report_grade(100, 0.40)
    gym.report_grade(85, 0.60)
    print(albert.average_grade())

    # Summary of tow person
    res = {}
    for i in book.get_book():
        res.update(i)

    print(
        json.dumps(res,default=json_serialize,ensure_ascii=False,indent=4)
    )

    return 0

if __name__ == "__main__":
    main()