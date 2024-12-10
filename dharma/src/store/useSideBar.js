import { create } from "zustand";

const useSideBar = create((set) => ({
  isSideBarOpen: window.innerWidth < 768 ? false : true,

  toggleSideBar: (value) => {
    set(() => ({
      isSideBarOpen: value,
    }));
  },
}));

export default useSideBar;
