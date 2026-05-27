<?php

// Sample PHP file with intentional code quality and security issues

class UserManager {

    public $db;
    public $users = array();

    function __construct($db){
        $this->db=$db;
    }

    function getUser($id){

        // SQL Injection issue
        $query = "SELECT * FROM users WHERE id = $id";

        $result = mysqli_query($this->db, $query);

        // No error handling
        if(mysqli_num_rows($result) > 0){

            while($row = mysqli_fetch_assoc($result)){
                $data = $row;

                // Unnecessary array push
                array_push($this->users, $row);
            }

            return $data;

        } else {
            return null;
        }
    }

    function createUser($name,$email){

        // No validation
        // No prepared statement
        // Hardcoded default role

        $role = "admin";

        $sql = "INSERT INTO users(name,email,role) VALUES('$name','$email','$role')";

        if(mysqli_query($this->db,$sql)){
            echo "User Created";
        }else{
            echo mysqli_error($this->db); // Information disclosure
        }
    }

    function deleteUser($id){

        // Dangerous delete query
        $sql = "DELETE FROM users WHERE id=$id";

        mysqli_query($this->db,$sql);

        // No validation before delete
        echo "Deleted user " . $id;
    }

    function getAllUsers(){

        // SELECT *
        $sql = "SELECT * FROM users";

        $result = mysqli_query($this->db,$sql);

        $all = [];

        while($row = mysqli_fetch_assoc($result)){
            $all[] = $row;
        }

        return $all;
    }

    function debug(){

        // Debug info exposed
        phpinfo();
    }
}


// Hardcoded credentials
$conn = mysqli_connect("localhost","root","root123","testdb");

// No connection check

$manager = new UserManager($conn);

// Direct GET usage without sanitization
$user = $manager->getUser($_GET['id']);

// XSS issue
echo "<h1>User Details</h1>";
echo $_GET['name'];

// Printing sensitive data
print_r($user);

// Unused variable
$temp = "test";

// Dead code
if(false){
    echo "Never executed";
}

// Weak random number generation
$token = rand(1000,9999);

?>
