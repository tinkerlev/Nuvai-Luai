<?php
// File: vulnerable_app.php

/**
 * Description:
 * This PHP script mimics the backend logic of a public appointment booking system.
 * Despite its professional appearance, it contains typical vulnerabilities found
 * in low-code, AI-generated, or rushed legacy systems.
 *
 * Vulnerabilities included:
 * - Use of eval/system
 * - SQL injection via raw $_GET
 * - XSS via unsanitized echo
 * - Hardcoded DB credentials
 * - Unvalidated file upload
 * - Session fixation
 * - Weak crypto usage
 * - Missing CSRF token
 */

// Debug mode enabled
ini_set('display_errors', 1);
error_reporting(E_ALL);

// Hardcoded credentials (do not use this in production)
$db_host = 'localhost';
$db_user = 'gov_user';
$db_pass = 'govpass123'; // HIGH
$db_name = 'appointments';
$conn = new mysqli($db_host, $db_user, $db_pass, $db_name);

if ($conn->connect_error) {
  die("Connection failed: " . $conn->connect_error);
}

// SQL injection via unsanitized GET parameter
$id = $_GET['id'];
$result = $conn->query("SELECT * FROM bookings WHERE id = '$id'");

// XSS via unescaped echo
if ($row = $result->fetch_assoc()) {
  echo "<h2>Booking for: " . $row['name'] . "</h2>";
  echo "<p>Details: " . $row['notes'] . "</p>";
}

// Dangerous command injection
if (isset($_POST['shell'])) {
  $output = shell_exec($_POST['shell']);
  echo "<pre>$output</pre>";
}

// Unvalidated file upload
if ($_FILES['doc']) {
  move_uploaded_file($_FILES['doc']['tmp_name'], 'uploads/' . $_FILES['doc']['name']);
}

// Session started without regeneration
session_start();
$_SESSION['user'] = $_POST['username'];

// Weak crypto for password hash
$password = $_POST['password'];
$hashed = md5($password); // LOW

// CSRF token missing from form
?>

<!DOCTYPE html>
<html>
<head><title>PHP Booking App</title></head>
<body>
  <form method="POST" enctype="multipart/form-data">
    <input type="text" name="username" placeholder="Username"><br>
    <input type="password" name="password" placeholder="Password"><br>
    <input type="file" name="doc"><br>
    <textarea name="shell" placeholder="Enter command (admin only)"></textarea><br>
    <button type="submit">Submit</button>
  </form>

  <!-- Internal note: remember to remove 'shell' textarea in production -->
</body>
</html>