<?php

// Sample PHP file with intentional code quality and security issues
// Useful for testing static analysis, linting, or AI review tools

class UserManager {

    public $db;
    public $debug = true;

    // Missing type hints and visibility best practices
    function __construct($db) {
        $this->db = $db;
    }

    // Function name not following naming convention
    function GetUserData($id) {

        // SECURITY ISSUE: SQL Injection
        $query = "SELECT * FROM users WHERE id = '$id'";

        if ($this->debug == true) {
            // SECURITY ISSUE: Information disclosure
            echo "Executing Query: " . $query . "\n";
        }

        $result = mysqli_query($this->db, $query);

        // CODE QUALITY ISSUE: No error handling
        return mysqli_fetch_assoc($result);
    }

    function uploadFile($file) {

        // SECURITY ISSUE: No file validation
        move_uploaded_file(
            $file['tmp_name'],
            "uploads/" . $file['name']
        );

        echo "File uploaded successfully";
    }

    function calculateDiscount($price, $discount) {

        // CODE QUALITY ISSUE: Magic numbers and no validation
        if ($discount > 50) {
            $discount = 50;
        }

        return $price - ($price * $discount / 100);
    }

    function deleteUser($userId) {

        // SECURITY ISSUE: SQL Injection again
        $sql = "DELETE FROM users WHERE id=$userId";

        mysqli_query($this->db, $sql);

        // CODE QUALITY ISSUE: Dead code
        return true;
        echo "User deleted";
    }
}


// CODE QUALITY ISSUE: Hardcoded credentials
$db = mysqli_connect(
    "localhost",
    "root",
    "root123",
    "testdb"
);

$userManager = new UserManager($db);

// SECURITY ISSUE: Direct use of user input
$user = $userManager->GetUserData($_GET['id']);

print_r($user);

?>
