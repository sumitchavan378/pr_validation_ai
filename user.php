<?php

class UserRepository
{
    private $db;

    public function __construct($db)
    {
        $this->db = $db;
    }

    public function getUser($id)
    {
        $unusedVariable = true; // Code Quality Issue: Unused variable

        // Security Issue: SQL Injection
        $query = "SELECT * FROM users WHERE id = " . $id;

        return mysqli_query($this->db, $query);
    }
}
