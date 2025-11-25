def binary_search(nums,target):
    left=0
    right=len(nums)-1

    while left <= right:
        mid= (left+right)//2
        if nums[mid] > target:
            right = mid-1
        elif nums[mid] < target:
            left = mid+1 
        else:
            return mid 
        
    return -1 

nums=[1,2,3,4,5,6,7,8,9,10,10,10,10,11,12,13,14,15,15]
target=10
#binary_search(nums, target)


def last_occurence(nums, target):
    left=0
    right=len(nums)-1
    ans=-1

    while left <= right:
            
            mid= (left+right)//2

            if nums[mid] == target:
                ans=mid   
                left = mid+1
            elif nums[mid] < target:
                left = mid+1 
            else:
                right = mid-1
            
    return ans

last_occurence(nums,target)


def first_occurence(nums, target):
    left=0
    right=len(nums)-1
    ans=-1

    while left <= right:
            
            mid= (left+right)//2

            if nums[mid] == target:
                ans=mid     
                right = mid-1
            elif nums[mid] < target:
                left = mid+1 
            else:
                right = mid-1
            
    return ans

#first_occurence(nums,target)


def count_occurence(nums, target):
     
     first=first_occurence(nums,target)
     if first ==-1:
       return 0
     else:
        last=last_occurence(nums,target)
        count= (last-first)+1
        return count

count_occurence(nums,target)