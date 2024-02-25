import SearchBar from "./SearchBar";
import ClassList from "../Class/ClassList";

export default function StudentPage() {
  const classes = ['Math 101', 'Physics 202', 'Chemistry 303', 'Biology 404'];

  return (
    <div className="flex flex-col">
      <div > 
        <SearchBar />
      </div>
      <div className="pt-16"> 
        <ClassList classes={classes} />
      </div>
    </div>
  );
}
