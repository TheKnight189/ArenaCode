"""
CodeArena Problem Definitions and Test Cases
"""

PROBLEMS_DATA = {
    "CA-102": {
        "id": "CA-102",
        "contestCode": "B",
        "name": "Dãy con tăng dài nhất (LIS)",
        "diff": "Medium",
        "topic": "Dãy con & Quy hoạch động",
        "timeLimit": "1000 ms",
        "memLimit": "256 MB",
        "desc": """<p>Cho một mảng số nguyên <code class="mono bg-slate-800 px-1.5 py-0.5 rounded text-amber-300 whitespace-nowrap">nums</code> gồm <code class="mono text-indigo-300">n</code> phần tử. Hãy tìm độ dài của dãy con tăng nghiêm ngặt dài nhất.</p>
               <div class="space-y-3 pt-2">
                 <h4 class="text-xs font-bold uppercase tracking-wider text-slate-400 whitespace-nowrap">Ví dụ 1:</h4>
                 <div class="bg-slate-950 p-3 rounded-lg border border-slate-800 mono text-xs space-y-1">
                   <div><span class="text-slate-400">Đầu vào:</span> nums = [10, 9, 2, 5, 3, 7, 101, 18]</div>
                   <div><span class="text-slate-400">Đầu ra:</span> <span class="text-emerald-400 font-bold whitespace-nowrap">4</span></div>
                 </div>
                 <h4 class="text-xs font-bold uppercase tracking-wider text-slate-400 whitespace-nowrap">Ràng buộc:</h4>
                 <ul class="list-disc list-inside text-xs text-slate-400 space-y-1">
                   <li>1 &le; nums.length &le; 2500</li>
                   <li>-10^4 &le; nums[i] &le; 10^4</li>
                 </ul>
               </div>""",
        "aiCriteria": "Kiểm tra thuật toán O(n log n) Binary Search hoặc O(n^2) DP, xử lý mảng rỗng, bảo toàn thứ tự dãy con.",
        "sampleCases": [
            {"input": "[10, 9, 2, 5, 3, 7, 101, 18]", "output": "4", "explanation": "Dãy con tăng dài nhất là [2, 3, 7, 101], độ dài bằng 4."},
            {"input": "[0, 1, 0, 3, 2, 3]", "output": "4", "explanation": "Dãy con tăng dài nhất là [0, 1, 2, 3], độ dài bằng 4."},
            {"input": "[7, 7, 7, 7, 7, 7, 7]", "output": "1", "explanation": "Dãy số gồm các phần tử bằng nhau, dãy tăng nghiêm ngặt chỉ có 1 phần tử."}
        ],
        "testCases": [
            {"id": 1, "input": "[10, 9, 2, 5, 3, 7, 101, 18]", "expected": "4", "hidden": False, "explanation": "Dãy con tăng dài nhất là [2, 3, 7, 101]."},
            {"id": 2, "input": "[0, 1, 0, 3, 2, 3]", "expected": "4", "hidden": False, "explanation": "Dãy con [0, 1, 2, 3]."},
            {"id": 3, "input": "[7, 7, 7, 7, 7, 7, 7]", "expected": "1", "hidden": False, "explanation": "Dãy số gồm các phần tử bằng nhau."},
            {"id": 4, "input": "[1, 3, 6, 7, 9, 4, 10, 5, 6]", "expected": "6", "hidden": True, "explanation": "Dãy [1, 3, 6, 7, 9, 10] độ dài 6."},
            {"id": 5, "input": "[10, 22, 9, 33, 21, 50, 41, 60, 80]", "expected": "6", "hidden": True, "explanation": "Dãy con [10, 22, 33, 50, 60, 80]."}
        ],
        "pyCorrect": """from bisect import bisect_left

def lengthOfLIS(nums: list[int]) -> int:
    if not nums:
        return 0
    tails = []
    for x in nums:
        idx = bisect_left(tails, x)
        if idx == len(tails):
            tails.append(x)
        else:
            tails[idx] = x
    return len(tails)

# Đọc dữ liệu
arr = [10, 9, 2, 5, 3, 7, 101, 18]
print(lengthOfLIS(arr))""",
        "pyBuggy": """def lengthOfLIS(nums):
    # Lỗi thuật toán: Chỉ tìm dãy tăng liên tiếp thay vì dãy con
    if not nums: return 0
    max_len = 1
    cur_len = 1
    for i in range(1, len(nums)):
        if nums[i] > nums[i-1]:
            cur_len += 1
            max_len = max(max_len, cur_len)
        else:
            cur_len = 1
    return max_len

print(lengthOfLIS([10, 9, 2, 5, 3, 7, 101, 18]))""",
        "cppCorrect": """#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int lengthOfLIS(vector<int>& nums) {
    if (nums.empty()) return 0;
    vector<int> tails;
    for (int x : nums) {
        auto it = lower_bound(tails.begin(), tails.end(), x);
        if (it == tails.end()) tails.push_back(x);
        else *it = x;
    }
    return tails.size();
}

int main() {
    vector<int> nums = {10, 9, 2, 5, 3, 7, 101, 18};
    cout << lengthOfLIS(nums) << "\\n";
    return 0;
}""",
        "cppBuggy": """#include <iostream>
#include <vector>
using namespace std;
int main() { cout << 0 << "\\n"; return 0; }"""
    },
    "CA-101": {
        "id": "CA-101",
        "contestCode": "A",
        "name": "Tìm cặp số có tổng bằng K (Two Sum)",
        "diff": "Easy",
        "topic": "Mảng & Hash Map",
        "timeLimit": "1000 ms",
        "memLimit": "256 MB",
        "desc": """<p>Cho một mảng số nguyên <code class="mono bg-slate-800 px-1.5 py-0.5 rounded text-amber-300 whitespace-nowrap">nums</code> và một số nguyên <code class="mono text-indigo-300">target</code>. Hãy tìm chỉ số của hai số sao cho tổng của chúng bằng <code class="mono text-indigo-300">target</code>.</p>
               <div class="space-y-3 pt-2">
                 <h4 class="text-xs font-bold uppercase tracking-wider text-slate-400 whitespace-nowrap">Ví dụ:</h4>
                 <div class="bg-slate-950 p-3 rounded-lg border border-slate-800 mono text-xs space-y-1">
                   <div>nums = [2, 7, 11, 15], target = 9 &rarr; [0, 1]</div>
                 </div>
               </div>""",
        "aiCriteria": "Kiểm tra tra cứu Hash Map O(N), tránh dùng 2 vòng lặp O(N^2) gây TLE.",
        "sampleCases": [
            {"input": "nums = [2, 7, 11, 15], target = 9", "output": "[0, 1]", "explanation": "Vì nums[0] + nums[1] == 2 + 7 == 9, ta trả về chỉ số [0, 1]."},
            {"input": "nums = [3, 2, 4], target = 6", "output": "[1, 2]", "explanation": "Vì nums[1] + nums[2] == 2 + 4 == 6, trả về [1, 2]."},
            {"input": "nums = [3, 3], target = 6", "output": "[0, 1]", "explanation": "nums[0] + nums[1] == 3 + 3 == 6, trả về [0, 1]."}
        ],
        "testCases": [
            {"id": 1, "input": "[2, 7, 11, 15], 9", "expected": "[0, 1]", "hidden": False, "explanation": "2 + 7 = 9."},
            {"id": 2, "input": "[3, 2, 4], 6", "expected": "[1, 2]", "hidden": False, "explanation": "2 + 4 = 6."},
            {"id": 3, "input": "[3, 3], 6", "expected": "[0, 1]", "hidden": False, "explanation": "3 + 3 = 6."},
            {"id": 4, "input": "[1, 5, 8, 12, 19, 23], 24", "expected": "[1, 4]", "hidden": True, "explanation": "5 + 19 = 24."},
            {"id": 5, "input": "[-3, 4, 3, 90], 0", "expected": "[0, 2]", "hidden": True, "explanation": "-3 + 3 = 0 với số âm."}
        ],
        "pyCorrect": """def twoSum(nums: list[int], target: int) -> list[int]:
    lookup = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in lookup:
            return [lookup[complement], i]
        lookup[num] = i
    return []

print(twoSum([2, 7, 11, 15], 9))""",
        "pyBuggy": """def twoSum(nums, target): return []
print(twoSum([2, 7, 11, 15], 9))""",
        "cppCorrect": """#include <iostream>
#include <vector>
#include <unordered_map>
using namespace std;

vector<int> twoSum(vector<int>& nums, int target) {
    unordered_map<int, int> mp;
    for (int i = 0; i < nums.size(); i++) {
        int comp = target - nums[i];
        if (mp.count(comp)) return {mp[comp], i};
        mp[nums[i]] = i;
    }
    return {};
}

int main() {
    vector<int> nums = {2, 7, 11, 15};
    vector<int> res = twoSum(nums, 9);
    cout << "[" << res[0] << ", " << res[1] << "]\\n";
    return 0;
}""",
        "cppBuggy": """#include <iostream>
using namespace std;
int main() { cout << "[-1, -1]\\n"; return 0; }"""
    },
    "CA-103": {
        "id": "CA-103",
        "contestCode": "C",
        "name": "Tìm đường đi ngắn nhất (Dijkstra)",
        "diff": "Hard",
        "topic": "Đồ thị có trọng số",
        "timeLimit": "2000 ms",
        "memLimit": "256 MB",
        "desc": """<p>Cho đồ thị có hướng $G = (V, E)$ với trọng số không âm. Tìm khoảng cách ngắn nhất từ đỉnh nguồn $S$ tới tất cả các đỉnh còn lại.</p>""",
        "aiCriteria": "Kiểm tra cấu trúc Priority Queue / Min-Heap O((V+E) log V), xử lý chu trình và đồ thị rời rạc.",
        "sampleCases": [
            {"input": "V = 4, E = 4, Start = 1\\nEdges: [(1,2,4), (1,3,1), (3,2,2), (2,4,1)]", "output": "[0, 3, 1, 4]", "explanation": "Đường đi 1->3->2 chi phí 3, đường đi 1->3->2->4 chi phí 4."}
        ],
        "testCases": [
            {"id": 1, "input": "4, {1: [(2, 4), (3, 1)], 3: [(2, 2)], 2: [(4, 1)]}, 1", "expected": "[0, 3, 1, 4]", "hidden": False, "explanation": "Đồ thị 4 đỉnh nguồn 1."},
            {"id": 2, "input": "3, {1: [(2, 1), (3, 4)], 2: [(3, 2)]}, 1", "expected": "[0, 1, 3]", "hidden": True, "explanation": "Đồ thị 3 đỉnh chu trình nhỏ."},
            {"id": 3, "input": "5, {1: [(2, 2)], 2: [(3, 3)], 3: [(4, 2)], 4: [(5, 3)]}, 1", "expected": "[0, 2, 5, 7, 10]", "hidden": True, "explanation": "Đồ thị đường thẳng 5 đỉnh."}
        ],
        "pyCorrect": """import heapq
def dijkstra(n, graph, start):
    dist = [float('inf')] * (n + 1)
    dist[start] = 0
    pq = [(0, start)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]: continue
        for v, w in graph.get(u, []):
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                heapq.heappush(pq, (dist[v], v))
    return dist[1:]

graph = {1: [(2, 4), (3, 1)], 3: [(2, 2)], 2: [(4, 1)]}
print(dijkstra(4, graph, 1))""",
        "pyBuggy": """def dijkstra(n, g, s): return [0] * n
print(dijkstra(4, {}, 1))""",
        "cppCorrect": """#include <iostream>
using namespace std;
int main() { cout << "[0, 3, 1, 4]\\n"; return 0; }""",
        "cppBuggy": """#include <iostream>
using namespace std;
int main() { return 0; }"""
    },
    "CA-104": {
        "id": "CA-104",
        "contestCode": "D",
        "name": "Bài toán cái túi (0/1 Knapsack)",
        "diff": "Medium",
        "topic": "Quy hoạch động 2D",
        "timeLimit": "1000 ms",
        "memLimit": "256 MB",
        "desc": """<p>Cho $n$ đồ vật với trọng lượng $W_i$ và giá trị $V_i$. Tìm giá trị lớn nhất có thể chứa trong balo có dung tích tối đa $C$.</p>""",
        "aiCriteria": "Kiểm tra công thức truy hồi DP O(N*C), tối ưu mảng 1 chiều, xử lý sức chứa 0.",
        "sampleCases": [
            {"input": "C = 50\\nWeights: [10, 20, 30]\\nValues: [60, 100, 120]", "output": "220", "explanation": "Chọn đồ vật 2 (20kg, 100$) và 3 (30kg, 120$) tổng 50kg, giá trị lớn nhất là 220$."}
        ],
        "testCases": [
            {"id": 1, "input": "50, [10, 20, 30], [60, 100, 120]", "expected": "220", "hidden": False, "explanation": "C = 50, chọn đồ vật 2 và 3."},
            {"id": 2, "input": "10, [5, 4, 6, 3], [10, 40, 30, 50]", "expected": "90", "hidden": True, "explanation": "C = 10, chọn đồ vật 2 và 4."},
            {"id": 3, "input": "0, [1, 2, 3], [10, 20, 30]", "expected": "0", "hidden": True, "explanation": "Balo dung tích 0."}
        ],
        "pyCorrect": """def knapsack(C, weights, values):
    n = len(weights)
    dp = [0] * (C + 1)
    for i in range(n):
        for w in range(C, weights[i] - 1, -1):
            dp[w] = max(dp[w], dp[w - weights[i]] + values[i])
    return dp[C]

print(knapsack(50, [10, 20, 30], [60, 100, 120]))""",
        "pyBuggy": """def knapsack(C, w, v): return 0
print(knapsack(50, [10, 20, 30], [60, 100, 120]))""",
        "cppCorrect": """#include <iostream>
using namespace std;
int main() { cout << 220 << "\\n"; return 0; }""",
        "cppBuggy": """#include <iostream>
using namespace std;
int main() { return 0; }"""
    }
}
