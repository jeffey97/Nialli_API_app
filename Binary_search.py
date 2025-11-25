def binary_search(nums,target):
    left = 0
    right = len(nums)-1

    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return "Target found at index " + str(mid)
        elif nums[mid] < target:
            left = mid + 1
        else:
            right  = mid -1        
    return "Target not found" 


nums = [1,3,5,6,9,12,17]
target = 17
binary_search(nums, target) 