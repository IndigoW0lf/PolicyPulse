import React from 'react';

const Navbar = () => {
    return (
        <nav>
            <h1>PolicyPulse</h1>
            <ul>
                <li><a href="/">Home</a></li>
                <li><a href="/Bills">Bills</a></li>
                <li><a href="/search">Search</a></li>
                <li><a href="/filter">Filter</a></li>
            </ul>
        </nav>
    );
}

export default Navbar;