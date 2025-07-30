import React from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import MainWrapper from "./layouts/MainWrapper";
import PrivateRoute from "./layouts/PrivateRoute";
import Register from "../src/views/auth/Register";
import Login from "../src/views/auth/Login";
import Logout from "./views/auth/Logout";
import ForgotPassword from "./views/auth/ForgotPassword";
import CreateNewPassword from "./views/auth/CreateNewPassword";
import Index from "./views/base/Index.jsx";
import Checkout from "./views/base/Checkout";
import Cart from "./views/base/Cart";
import Success from "./views/base/Success";
import Search from "./views/base/Search";
import CourseDetail from "./views/base/CourseDetail";

// student
import ChangePasswordStudent from "./views/student/ChangePassword.jsx";
import CourseDetailStudent from "./views/student/CourseDetail";
import Courses from "./views/student/Courses";
import DashboardStudent from "./views/student/Dashboard";
import StudentProfile from "./views/student/Profile";
import QA from "./views/student/QA";
import QADetail from "./views/student/QADetail";
import StudentCourseLectureDetail from "./views/student/StudentCourseLectureDetail";
import Wishlist from "./views/student/Wishlist";

// instructor
import ChangePasswordInstructor from "./views/instructor/ChangePassword.jsx";
import Coupon from "./views/instructor/Coupon.jsx";
import CourseCreate from "./views/instructor/CourseCreate.jsx";
import CourseEdit from "./views/instructor/CourseEdit.jsx";
import CoursesInstructor from "./views/instructor/Courses.jsx";
import DashBoardInstructor from "./views/instructor/Dashboard.jsx";
import Earning from "./views/instructor/Earning.jsx";
import Orders from "./views/instructor/Orders.jsx";
// import ProfileInstructor from "./views/instructor/ProfileInstructor.jsx";
import QAInstructor from "./views/instructor/QA.jsx";
import QADetailInstructor from "./views/instructor/QADetail.jsx";
import Review from "./views/instructor/Review.jsx";

function App() {
  return (
    <BrowserRouter>
      <MainWrapper>
        <Routes>
          {/* add a public route so that I can show the registration page */}
          <Route path="/register/" element={<Register />} />
          <Route path="/login/" element={<Login />} />
          <Route path="/logout/" element={<Logout />} />
          <Route path="/forgot-password/" element={<ForgotPassword />} />
          <Route path="/create-new-password/" element={<CreateNewPassword />} />
          {/* Base Routes */}
          <Route path="" element={<Index />} />
          <Route path="/checkout/" element={<Checkout />} />
          <Route path="/cart/" element={<Cart />} />
          <Route path="/success/" element={<Success />} />
          <Route path="/search/" element={<Search />} />
          <Route path="/CourseDetail/" element={<CourseDetail />} />

          {/* student routes */}
          <Route
            path="/ChangePasswordStudent/"
            element={<ChangePasswordStudent />}
          />
          <Route
            path="/CourseDetailStudent/"
            element={<CourseDetailStudent />}
          />
          <Route path="/courses/" element={<Courses />} />
          <Route path="/DashboardStudent/" element={<DashboardStudent />} />
          <Route path="/StudentProfile/" element={<StudentProfile />} />
          <Route path="/QA/" element={<QA />} />
          <Route path="/QADetail/" element={<QADetail />} />
          <Route
            path="/StudentCourseLectureDetail/"
            element={<StudentCourseLectureDetail />}
          />
          <Route path="/wishlist/" element={<Wishlist />} />

          {/* Intructor routes */}

          <Route
            path="/ChangePasswordInstructor/"
            element={<ChangePasswordInstructor />}
          />
          <Route path="/Coupon/" element={<Coupon />} />
          <Route path="/CourseCreate/" element={<CourseCreate />} />
          <Route path="/CourseEdit/" element={<CourseEdit />} />
          <Route path="/CoursesInstructor/" element={<CoursesInstructor />} />
          <Route
            path="/DashBoardInstructor/"
            element={<DashBoardInstructor />}
          />
          <Route path="/Earning/" element={<Earning />} />
          <Route path="/Orders/" element={<Orders />} />
          <Route path="/ProfileInstructor/" element={<ProfileInstructor />} />
          <Route path="/QAInstructor/" element={<QAInstructor />} />
          <Route path="/QADetailInstructor/" element={<QADetailInstructor />} />
          <Route path="/Review/" element={<Review />} />
        </Routes>
      </MainWrapper>
    </BrowserRouter>
  );
}

export default App;
