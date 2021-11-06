package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strconv"

	_ "github.com/lib/pq"
)

type User struct {
	Username string `json:"username"`
	Password string `json:"password"`
	Id       int    `json:"id"`
}

type Workspace struct {
	Id   int    `json:"id"`
	Name string `json:"workspace_name"`
}

type Location struct {
	Id          int `json:"id"`
	WorkspaceId int `json:"workspace_id"`
	Distance    int `json:"distance"`
	Angle       int `json:"angle"`
}

type Route struct {
	Id         int     `json:"id"`
	Route_id   int     `json:"route_id`
	Name       string  `json:"name"`
	Angle      int     `json:"angle"`
	Distance   float64 `json:"distance"`
	NewId      int     `json:"new_id"`
	NewRoute   int     `json:"new_route"`
	AltRoute   int     `json:"alt_route"`
	AltRouteId int     `json:"alt_route_id"SSSS`
}

type ById struct {
	ById int `json:"ById"`
}

const (
	host     = "127.0.0.1"
	port     = 5432
	user     = "postgres"
	password = "Roy040571"
	dbname   = "SpheroDSR"
)

func OpenConnection() *sql.DB {
	psqlInfo := fmt.Sprintf("host=%s port=%d user=%s "+
		"password=%s dbname=%s sslmode=disable",
		host, port, user, password, dbname)

	db, err := sql.Open("postgres", psqlInfo)
	if err != nil {
		panic(err)
	}

	err = db.Ping()
	if err != nil {
		panic(err)
	}

	return db
}

func GETUsers(w http.ResponseWriter, r *http.Request) {
	db := OpenConnection()

	rows, err := db.Query("SELECT * FROM users")
	if err != nil {
		log.Fatal(err)
	}

	var users []User

	for rows.Next() {
		var user User
		rows.Scan(&user.Id, &user.Username, &user.Password)
		users = append(users, user)
	}
	fmt.Println(users)

	peopleBytes, _ := json.MarshalIndent(users, "", "\t")

	w.Header().Set("Content-Type", "application/json")
	w.Write(peopleBytes)

	defer rows.Close()
	defer db.Close()
}

func GETUserById(w http.ResponseWriter, r *http.Request) {
	db := OpenConnection()

	var u User
	err := json.NewDecoder(r.Body).Decode(&u)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	rows, err := db.Query("SELECT * FROM users WHERE id=$1", u.Id)

	if err != nil {
		log.Fatal(err)
	}

	var users []User

	for rows.Next() {
		var user User
		rows.Scan(&user.Id, &user.Username, &user.Password)
		users = append(users, user)
	}
	fmt.Println(users)

	peopleBytes, _ := json.MarshalIndent(users, "", "\t")

	w.Header().Set("Content-Type", "application/json")
	w.Write(peopleBytes)

	defer rows.Close()
	defer db.Close()
}

func GETUserByName(w http.ResponseWriter, r *http.Request) {
	db := OpenConnection()

	var u User
	err := json.NewDecoder(r.Body).Decode(&u)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	rows, err := db.Query("SELECT * FROM users WHERE userName=$1", u.Username)

	if err != nil {
		log.Fatal(err)
	}

	var users []User

	for rows.Next() {
		var user User
		rows.Scan(&user.Id, &user.Username, &user.Password)
		users = append(users, user)
	}
	fmt.Println(users)

	peopleBytes, _ := json.MarshalIndent(users, "", "\t")

	w.Header().Set("Content-Type", "application/json")
	w.Write(peopleBytes)

	defer rows.Close()
	defer db.Close()
}

func POSTCreateUser(w http.ResponseWriter, r *http.Request) {
	db := OpenConnection()

	var u User
	err := json.NewDecoder(r.Body).Decode(&u)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	sqlStatement := `insert into users (userName, password) VALUES ($1, $2)`
	_, err = db.Exec(sqlStatement, u.Username, u.Password)
	if err != nil {
		w.WriteHeader(http.StatusBadRequest)
		panic(err)
	}

	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, "user '"+u.Username+"' has been created")
	defer db.Close()
}

func DELETEUserById(w http.ResponseWriter, r *http.Request) {
	db := OpenConnection()

	var u User
	err := json.NewDecoder(r.Body).Decode(&u)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	sqlStatement := `delete from users where id=$1`
	_, err = db.Exec(sqlStatement, u.Id)
	if err != nil {
		w.WriteHeader(http.StatusBadRequest)
		panic(err)
	}

	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, "user '"+u.Username+"' has been deleted")
	defer db.Close()
}

func DELETEUserByUsername(w http.ResponseWriter, r *http.Request) {
	db := OpenConnection()

	var u User
	err := json.NewDecoder(r.Body).Decode(&u)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	sqlStatement := `delete from users where userName=$1`
	_, err = db.Exec(sqlStatement, u.Username)
	if err != nil {
		w.WriteHeader(http.StatusBadRequest)
		panic(err)
	}
	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, "user '"+u.Username+"' has been deleted")
	defer db.Close()
}

func UPDATEUser(w http.ResponseWriter, r *http.Request) {
	db := OpenConnection()

	var u User
	err := json.NewDecoder(r.Body).Decode(&u)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	sqlStatement := `UPDATE users SET username=$2, password=$3 WHERE id=$1;`
	_, err = db.Exec(sqlStatement, u.Id, u.Username, u.Password)
	if err != nil {
		w.WriteHeader(http.StatusBadRequest)
		panic(err)
	}
	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, "User has been changed to '"+u.Username+"' with as password '"+u.Password+"'")
	defer db.Close()
}

func GETWorkspaces(w http.ResponseWriter, r *http.Request) {
	db := OpenConnection()

	rows, err := db.Query("SELECT * FROM workspaces")
	if err != nil {
		log.Fatal(err)
	}

	var workspaces []Workspace

	for rows.Next() {
		var workspace Workspace
		rows.Scan(&workspace.Id, &workspace.Name)
		workspaces = append(workspaces, workspace)
	}
	fmt.Println(workspaces)

	peopleBytes, _ := json.MarshalIndent(workspaces, "", "\t")

	w.Header().Set("Content-Type", "application/json")
	w.Write(peopleBytes)

	defer rows.Close()
	defer db.Close()
}

func GETWorkspaceById(w http.ResponseWriter, r *http.Request) {
	db := OpenConnection()

	var ws Workspace
	err := json.NewDecoder(r.Body).Decode(&ws)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	rows, err := db.Query("SELECT * FROM workspaces WHERE id=$1", ws.Id)

	if err != nil {
		log.Fatal(err)
	}

	var workspaces []Workspace

	for rows.Next() {
		var workspace Workspace
		rows.Scan(&workspace.Id, &workspace.Name)
		workspaces = append(workspaces, workspace)
	}
	fmt.Println(workspaces)

	peopleBytes, _ := json.MarshalIndent(workspaces, "", "\t")

	w.Header().Set("Content-Type", "application/json")
	w.Write(peopleBytes)

	defer rows.Close()
	defer db.Close()
}

func GETWorkspaceByName(w http.ResponseWriter, r *http.Request) {
	db := OpenConnection()

	var ws Workspace
	err := json.NewDecoder(r.Body).Decode(&ws)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	rows, err := db.Query("SELECT * FROM workspaces WHERE name=$1", ws.Name)

	if err != nil {
		log.Fatal(err)
	}

	var workspaces []Workspace

	for rows.Next() {
		var workspace Workspace
		rows.Scan(&workspace.Id, &workspace.Name)
		workspaces = append(workspaces, workspace)
	}
	fmt.Println(workspaces)

	peopleBytes, _ := json.MarshalIndent(workspaces, "", "\t")

	w.Header().Set("Content-Type", "application/json")
	w.Write(peopleBytes)

	defer rows.Close()
	defer db.Close()
}

func POSTCreateWorkspace(w http.ResponseWriter, r *http.Request) {
	db := OpenConnection()

	var ws Workspace
	err := json.NewDecoder(r.Body).Decode(&ws)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	sqlStatement := `insert into workspaces (name) VALUES ($1)`
	_, err = db.Exec(sqlStatement, ws.Name)
	if err != nil {
		w.WriteHeader(http.StatusBadRequest)
		panic(err)
	}
	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, "workspace '"+ws.Name+"' has been created")
	defer db.Close()
}

func DELETEWorkspaceById(w http.ResponseWriter, r *http.Request) {
	db := OpenConnection()

	var ws Workspace
	err := json.NewDecoder(r.Body).Decode(&ws)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	sqlStatement := `delete from workspaces where id=$1`
	_, err = db.Exec(sqlStatement, ws.Id)
	if err != nil {
		w.WriteHeader(http.StatusBadRequest)
		panic(err)
	} else {
		w.WriteHeader(http.StatusOK)
		fmt.Fprintf(w, "Workspace '"+ws.Name+"' has been deleted")
		defer db.Close()
	}
}

func DELETEWorkspaceByUsername(w http.ResponseWriter, r *http.Request) {
	db := OpenConnection()

	var ws Workspace
	err := json.NewDecoder(r.Body).Decode(&ws)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	sqlStatement := `delete from workspaces where name=$1`
	_, err = db.Exec(sqlStatement, ws.Name)
	if err != nil {
		w.WriteHeader(http.StatusBadRequest)
		panic(err)
	} else {
		w.WriteHeader(http.StatusOK)
		fmt.Fprintf(w, "Workspace '"+ws.Name+"' has been deleted")
		defer db.Close()
	}
}

func UPDATEWorkspace(w http.ResponseWriter, r *http.Request) {
	db := OpenConnection()

	var ws Workspace
	err := json.NewDecoder(r.Body).Decode(&ws)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	sqlStatement := `UPDATE workspaces SET name=$2 WHERE id=$1;`
	_, err = db.Exec(sqlStatement, ws.Id, ws.Name)
	if err != nil {
		w.WriteHeader(http.StatusBadRequest)
		panic(err)
	}
	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, "Workspace has been changed to '"+ws.Name+"'")
	defer db.Close()
}

func GETLocations(w http.ResponseWriter, r *http.Request) {
	db := OpenConnection()

	rows, err := db.Query("SELECT * FROM location_values")
	if err != nil {
		log.Fatal(err)
	}

	var locations []Location

	for rows.Next() {
		var location Location
		rows.Scan(&location.Id, &location.WorkspaceId, &location.Distance, &location.Angle)
		locations = append(locations, location)
	}
	fmt.Println(locations)

	peopleBytes, _ := json.MarshalIndent(locations, "", "\t")

	w.Header().Set("Content-Type", "application/json")
	w.Write(peopleBytes)

	defer rows.Close()
	defer db.Close()
}

func GETLocationById(w http.ResponseWriter, r *http.Request) {
	db := OpenConnection()

	var l Location
	err := json.NewDecoder(r.Body).Decode(&l)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	rows, err := db.Query("SELECT * FROM location_values WHERE id=$1", l.Id)

	if err != nil {
		log.Fatal(err)
	}

	var locations []Location

	for rows.Next() {
		var location Location
		rows.Scan(&location.Id, &location.WorkspaceId, &location.Distance, &location.Angle)
		locations = append(locations, location)
	}
	fmt.Println(locations)

	peopleBytes, _ := json.MarshalIndent(locations, "", "\t")

	w.Header().Set("Content-Type", "application/json")
	w.Write(peopleBytes)

	defer rows.Close()
	defer db.Close()
}

func GETLocationByWorkspaceId(w http.ResponseWriter, r *http.Request) {
	db := OpenConnection()

	var l Location
	err := json.NewDecoder(r.Body).Decode(&l)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	rows, err := db.Query("SELECT * FROM location_values WHERE workspace_id=$1", l.WorkspaceId)

	if err != nil {
		log.Fatal(err)
	}

	var locations []Location

	for rows.Next() {
		var location Location
		rows.Scan(&location.Id, &location.WorkspaceId, &location.Distance, &location.Angle)
		locations = append(locations, location)
	}
	fmt.Println(locations)

	peopleBytes, _ := json.MarshalIndent(locations, "", "\t")

	w.Header().Set("Content-Type", "application/json")
	w.Write(peopleBytes)

	defer rows.Close()
	defer db.Close()
}

func POSTCreateLocation(w http.ResponseWriter, r *http.Request) {
	db := OpenConnection()

	var l Location
	err := json.NewDecoder(r.Body).Decode(&l)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	sqlStatement := `insert into location_values ( workspace_id, distance, angle) VALUES ($1, $2, $3)`
	_, err = db.Exec(sqlStatement, l.WorkspaceId, l.Distance, l.Angle)
	if err != nil {
		w.WriteHeader(http.StatusBadRequest)
		fmt.Fprintf(w, "An error has occured for creating a location")
		panic(err)
	}
	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, "location has been created")
	defer db.Close()
}

func DELETELocationById(w http.ResponseWriter, r *http.Request) {
	db := OpenConnection()

	var l Location
	err := json.NewDecoder(r.Body).Decode(&l)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	sqlStatement := `delete from location_values where id=$1`
	_, err = db.Exec(sqlStatement, l.Id)
	if err != nil {
		w.WriteHeader(http.StatusBadRequest)
		panic(err)
	}

	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, "location has been deleted")
	defer db.Close()
}

func DELETEAllLocations(w http.ResponseWriter, r *http.Request) {
	db := OpenConnection()

	var l Location
	err := json.NewDecoder(r.Body).Decode(&l)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	sqlStatement := `delete from location_values where workspace_id=$1`
	_, err = db.Exec(sqlStatement, l.WorkspaceId)
	if err != nil {
		w.WriteHeader(http.StatusBadRequest)
		panic(err)
	}

	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, "location has been deleted")
	defer db.Close()
}

func UPDATELocation(w http.ResponseWriter, r *http.Request) {
	db := OpenConnection()

	var l Location
	err := json.NewDecoder(r.Body).Decode(&l)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	sqlStatement := `UPDATE location_values SET distance=$2, angle=$3 WHERE id=$1;`
	_, err = db.Exec(sqlStatement, l.Id, l.Distance, l.Angle)
	if err != nil {
		w.WriteHeader(http.StatusBadRequest)
		panic(err)
	}
	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, "Distance has been changed to: "+strconv.Itoa(l.Distance)+"\nAngle has been changed to: "+strconv.Itoa(l.Angle))
	defer db.Close()
}

func GETRoutes(w http.ResponseWriter, r *http.Request) {
	db := OpenConnection()

	rows, err := db.Query("SELECT * FROM full_route")
	if err != nil {
		log.Fatal(err)
	}

	var routes []Route

	for rows.Next() {
		var route Route
		rows.Scan(&route.Id, &route.Route_id, &route.Name, &route.Angle, &route.Distance, &route.AltRoute, &route.AltRouteId)
		routes = append(routes, route)
	}
	fmt.Println(routes)

	peopleBytes, _ := json.MarshalIndent(routes, "", "\t")

	w.Header().Set("Content-Type", "application/json")
	w.Write(peopleBytes)

	defer rows.Close()
	defer db.Close()
}

func GETRoutesById(w http.ResponseWriter, r *http.Request) {
	db := OpenConnection()

	var rt Route
	err := json.NewDecoder(r.Body).Decode(&rt)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	rows, err := db.Query("SELECT * FROM full_route WHERE route_id=$1", rt.Route_id)

	if err != nil {
		log.Fatal(err)
	}

	var routes []Route

	for rows.Next() {
		var route Route
		rows.Scan(&route.Id, &route.Route_id, &route.Name, &route.Angle, &route.Distance, &route.AltRoute, &route.AltRouteId)
		routes = append(routes, route)
	}
	fmt.Println(routes)

	peopleBytes, _ := json.MarshalIndent(routes, "", "\t")

	w.Header().Set("Content-Type", "application/json")
	w.Write(peopleBytes)

	defer rows.Close()
	defer db.Close()
}

func POSTCreateRoute(w http.ResponseWriter, r *http.Request) {
	db := OpenConnection()

	var rt Route
	err := json.NewDecoder(r.Body).Decode(&rt)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	sqlStatement := `insert into full_route (route_id, id, name, angle, distance, alt_route, alt_route_id) VALUES ($1, $2, $3, $4, $5, $6, $7)`
	_, err = db.Exec(sqlStatement, rt.Route_id, rt.Id, rt.Name, rt.Angle, rt.Distance, rt.AltRoute, rt.AltRouteId)
	if err != nil {
		w.WriteHeader(http.StatusBadRequest)
		fmt.Fprintf(w, "An error has occured for creating a route")
		panic(err)
	}
	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, "Route has been created")
	defer db.Close()
}

func DELETERouteById(w http.ResponseWriter, r *http.Request) {
	db := OpenConnection()

	var rt Route
	err := json.NewDecoder(r.Body).Decode(&rt)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	sqlStatement := `delete from full_route where id=$1`
	_, err = db.Exec(sqlStatement, rt.Id)
	if err != nil {
		w.WriteHeader(http.StatusBadRequest)
		panic(err)
	}

	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, "location has been deleted")
	defer db.Close()
}

func UPDATERoute(w http.ResponseWriter, r *http.Request) {
	db := OpenConnection()

	var rt Route
	err := json.NewDecoder(r.Body).Decode(&rt)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	sqlStatement := `UPDATE full_route SET id=$1, route_id=$2, name=$3, angle=$4, distance=$5, alt_route=$8, alt_route_id=$9 WHERE id=$6 and route_id=$7;`
	_, err = db.Exec(sqlStatement, rt.NewId, rt.NewRoute, rt.Name, rt.Angle, rt.Distance, rt.Id, rt.Route_id, rt.AltRoute, rt.AltRouteId)
	if err != nil {
		w.WriteHeader(http.StatusBadRequest)
		fmt.Fprintf(w, "An error has occured")
		panic(err)
	}
	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, "Values have been changed")
	defer db.Close()
}

func main() {

	http.HandleFunc("/users", GETUsers)
	http.HandleFunc("/users/by_id", GETUserById)
	http.HandleFunc("/users/by_name", GETUserByName)
	http.HandleFunc("/users/insert", POSTCreateUser)
	http.HandleFunc("/users/delete/user_by_id", DELETEUserById)
	http.HandleFunc("/users/delete/user_by_name", DELETEUserByUsername)
	http.HandleFunc("/users/update", UPDATEUser)

	http.HandleFunc("/workspaces", GETWorkspaces)
	http.HandleFunc("/workspaces/by_id", GETWorkspaceById)
	http.HandleFunc("/workspaces/by_name", GETWorkspaceByName)
	http.HandleFunc("/workspaces/insert", POSTCreateWorkspace)
	http.HandleFunc("/workspaces/delete/workspace_by_id", DELETEWorkspaceById)
	http.HandleFunc("/workspaces/delete/workspace_by_name", DELETEWorkspaceByUsername)
	http.HandleFunc("/workspaces/update", UPDATEWorkspace)

	http.HandleFunc("/locations", GETLocations)
	http.HandleFunc("/locations/by_id", GETLocationById)
	http.HandleFunc("/locations/by_workspace_id", GETLocationByWorkspaceId)
	http.HandleFunc("/locations/insert", POSTCreateLocation)
	http.HandleFunc("/locations/delete/location_by_id", DELETELocationById)
	http.HandleFunc("/locations/delete/all", DELETEAllLocations)
	http.HandleFunc("/locations/update", UPDATELocation)

	http.HandleFunc("/route", GETRoutes)
	http.HandleFunc("/route/by_id", GETRoutesById)
	http.HandleFunc("/route/insert", POSTCreateRoute)
	http.HandleFunc("/route/delete", DELETERouteById)
	http.HandleFunc("/route/update", UPDATERoute)

	log.Fatal(http.ListenAndServe(":8080", nil))
}
