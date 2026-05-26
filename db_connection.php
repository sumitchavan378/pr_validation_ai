<?php

// Sample PHP file with some intentional code quality issues
// Useful for testing linting, static analysis, or AI code review tools

class UserManager {

    public $db;

    function __construct($db){
        $this->db=$db;
    }

    function getUser($id){

        // SQL Injection issue
        $query = "SELECT * FROM users WHERE id = $id";

        $result = mysqli_query($this->db, $query);

        if(mysqli_num_rows($result) > 0){

            while($row = mysqli_fetch_assoc($result)){
                $data = $row;
            }

            return $data;

        } else {
            return null;
        }
    }

    function createUser($name,$email){

        // No validation
        // No prepared statement

        $sql = "INSERT INTO users(name,email) VALUES('$name','$email')";

        if(mysqli_query($this->db,$sql)){
            echo "User Created";
        }else{
            echo "Error";
        }
    }

    function deleteUser($id){

        // Dangerous delete query
        $sql = "DELETE FROM users WHERE id=$id";

        mysqli_query($this->db,$sql);
    }
}


// Hardcoded credentials
$conn = mysqli_connect("localhost","root","root123","testdb");

$manager = new UserManager($conn);

// Direct GET usage without sanitization
$user = $manager->getUser($_GET['id']);

print_r($user);

?>
