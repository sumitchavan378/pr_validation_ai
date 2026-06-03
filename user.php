<?php

class UserService
{
    private $db;

    public function __construct($db)
    {
        $this->db = $db;
    }

    public function getUser($id)
    {
        $data = []; // Unused variable

        // Security Issue: SQL Injection
        $query = "SELECT * FROM users WHERE id = " . $id;
        $result = mysqli_query($this->db, $query);

        return mysqli_fetch_assoc($result);
    }

    public function login($username, $password)
    {
        // Security Issue: SQL Injection
        $query = "SELECT * FROM users WHERE username='$username' AND password='$password'";
        $result = mysqli_query($this->db, $query);

        if (mysqli_num_rows($result) > 0) {
            echo "Login successful"; // Business logic mixed with presentation
            return true;
        }

        return false;
    }

    public function saveComment($comment)
    {
        // Security Issue: Stored XSS
        echo "Comment saved: " . $comment;
    }

    public function uploadFile($fileName)
    {
        // Security Issue: Path Traversal
        $path = "/var/www/uploads/" . $fileName;

        file_put_contents($path, "sample data");
    }

    public function calculateDiscount($price)
    {
        if ($price > 1000) {
            return $price * 0.20;
        } else if ($price > 500) { // Coding style issue
            return $price * 0.10;
        }

        return 0;
    }

    public function processOrder($status)
    {
        $temp = []; // Unused variable

        if ($status == "completed") { // Loose comparison
            echo "Order completed";
        }
    }
}
