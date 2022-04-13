-- phpMyAdmin SQL Dump
-- version 4.9.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Sep 11, 2020 at 04:36 PM
-- Server version: 5.5.64-MariaDB
-- PHP Version: 7.2.33

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `Repometer_Database`
--

-- --------------------------------------------------------

--
-- Table structure for table `Account_Data`
--

CREATE TABLE `Account_Data` (
  `customer` varchar(40) COLLATE utf8_bin DEFAULT NULL,
  `url` varchar(90) COLLATE utf8_bin DEFAULT NULL,
  `username` varchar(40) COLLATE utf8_bin DEFAULT NULL,
  `token` varchar(60) COLLATE utf8_bin DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

-- --------------------------------------------------------

--
-- Table structure for table `Customer_Data`
--

CREATE TABLE `Customer_Data` (
  `customer` varchar(40) COLLATE utf8_bin DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

-- --------------------------------------------------------

--
-- Table structure for table `Repository_Data`
--

CREATE TABLE `Repository_Data` (
  `url` varchar(90) COLLATE utf8_bin DEFAULT NULL,
  `username` varchar(40) COLLATE utf8_bin DEFAULT NULL,
  `owner` varchar(40) COLLATE utf8_bin DEFAULT NULL,
  `repository` varchar(40) COLLATE utf8_bin DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

-- --------------------------------------------------------

--
-- Table structure for table `Traffic_Data`
--

CREATE TABLE `Traffic_Data` (
  `url` varchar(90) COLLATE utf8_bin DEFAULT NULL,
  `username` varchar(40) COLLATE utf8_bin DEFAULT NULL,
  `owner` varchar(40) COLLATE utf8_bin DEFAULT NULL,
  `repository` varchar(40) COLLATE utf8_bin DEFAULT NULL,
  `timestamp` date DEFAULT NULL,
  `tag` varchar(20) COLLATE utf8_bin DEFAULT NULL,
  `value` varchar(20) COLLATE utf8_bin DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
