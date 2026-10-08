<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\BulkStoreUsersRequest;
use App\Models\User;
use Carbon\Carbon;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\Hash;

class UserController extends Controller
{
    private const DEFAULT_PER_PAGE = 50;
    private const MAX_PER_PAGE = 100;

    public function index(): JsonResponse
    {
        $paginator = User::query()
            ->orderBy('id')
            ->paginate($this->perPage($request));

        return $this->paginated($paginator);
    }

    public function emails(): JsonResponse
    {
        $paginator = User::query()
            ->select(['id', 'email'])
            ->orderBy('id')
            ->paginate($this->perPage($request));

        return $this->paginated($paginator);    }

    public function overTwenty(): JsonResponse
    {
        $cutoff = Carbon::now()->subYears(20)->startOfDay();

        $paginator = User::query()
            ->whereNotNull('birth_date')
            ->where('birth_date', '<=', $cutoff->toDateString())
            ->orderBy('id')
            ->paginate($this->perPage($request));

        return $this->paginated($paginator, [
            'cutoff_date' => $cutoff->toDateString(),
        ]);
    }

    public function bulkStore(BulkStoreUsersRequest $request): JsonResponse
    {
        $created = [];

        foreach ($request->validated()['users'] as $userData) {
            $created[] = User::create([
                'name' => $userData['name'],
                'email' => $userData['email'],
                'birth_date' => $userData['birth_date'],
                'password' => Hash::make($userData['password'] ?? 'password'),
            ]);
        }

        return response()->json([
            'message' => 'Se crearon 3 usuarios correctamente.',
            'users' => $created,
        ], 201);
    }

    private function perPage(Request $request): int
    {
        $perPage = (int) $request->query('per_page', self::DEFAULT_PER_PAGE);

        return max(1, min($perPage, self::MAX_PER_PAGE));
    }

    private function paginated(LengthAwarePaginator $paginator, array $extra = []): JsonResponse
    {
        return response()->json(array_merge($extra, [
            'total' => $paginator->total(),
            'page' => $paginator->currentPage(),
            'per_page' => $paginator->perPage(),
            'last_page' => $paginator->lastPage(),
            'data' => $paginator->items(),
        ]));
    }
}
