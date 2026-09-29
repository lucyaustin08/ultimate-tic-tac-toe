import { Link, Outlet, type RouteObject } from "react-router";
import { GamePage } from "./pages/GamePage";
import { HomePage } from "./pages/HomePage";

function Layout() {
  return (
    <div className="flex min-h-screen flex-col items-center gap-8 px-4 py-8">
      <header>
        <h1 className="text-3xl font-black">
          <Link to="/">Ultimate Tic-Tac-Toe</Link>
        </h1>
      </header>
      <main className="flex w-full flex-col items-center">
        <Outlet />
      </main>
    </div>
  );
}

export const routes: RouteObject[] = [
  {
    path: "/",
    element: <Layout />,
    children: [
      { index: true, element: <HomePage /> },
      { path: "games/:gameId", element: <GamePage /> },
    ],
  },
];
