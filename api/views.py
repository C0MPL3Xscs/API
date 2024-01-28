from django.db import connection
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from rest_framework.decorators import api_view
from rest_framework.response import Response
from . import OTP
from . import TokenGen as TG
import base64
import logging
import os
from rest_framework.decorators import parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
import zlib

@api_view(['POST'])
def logIn(request):
    email = request.query_params.get('email', '')
    password = request.query_params.get('password', '')
    Token = TG.generate_token()

    try:
        with connection.cursor() as cursor:
            # Use parameterized query to prevent SQL injection
            query = "SELECT * FROM users WHERE email = %s AND password = %s;"
            cursor.execute(query, [email, password])
            result = cursor.fetchall()
        if result:
            with connection.cursor() as cursor:
                query = "UPDATE users SET Token = %s WHERE email = %s AND password = %s;"
                cursor.execute(query, [Token, email, password])
                result = cursor.fetchall()
            # User with the given username and password exists
            # Extract all columns from the result
            data = {'rescode': '0001', 'message': 'User found', 'loginToken': Token}
            
        else:
            # User with the given username and password does not exist
            data = {'rescode': '0002', 'message': 'User not found'}

    except (IntegrityError, ValidationError) as e:
        # Handle any database integrity errors or validation errors
        data = {'rescode': 'error', 'message': str(e)}

    return Response(data)
    
@api_view(['POST'])
def validateToken(request):
    Token = request.query_params.get('Token', '')

    try:
        with connection.cursor() as cursor:
            # Use parameterized query to prevent SQL injection
            query = "SELECT * FROM users WHERE Token = %s;"
            cursor.execute(query, [Token])
            result = cursor.fetchall()
        if result:
            # User with the given username and password exists
            # Extract all columns from the result
            Token = result[0]
            data = {'rescode': '0001', 'message': 'User found', 'loginToken': Token[5]}
            
        else:
            # User with the given username and password does not exist
            data = {'rescode': '0002', 'message': 'User not found'}

    except (IntegrityError, ValidationError) as e:
        # Handle any database integrity errors or validation errors
        data = {'rescode': 'error', 'message': str(e)}

    return Response(data)
    
@api_view(['POST'])
def sendOTP(request):
    email = request.query_params.get('email', '')

    OTP.send_otp(email)
    
    data = {'rescode': '0001', 'message': 'OTP sent'}

    return Response(data)
    
@api_view(['POST'])
def verifyOTP(request):
    email = request.query_params.get('email', '')
    otp = request.query_params.get('otp', '')

    if OTP.verifyotp(email,otp):
   		data = {'rescode': '0001', 'message': 'OTP is correct'}
    else:
    	data = {'rescode': '0002', 'message': 'OTP is not correct'}

    return Response(data)

@api_view(['POST'])
def verifyUsername(request):
    username = request.query_params.get('username', '')

    try:
        with connection.cursor() as cursor:
            # Use parameterized query to prevent SQL injection
            query = "SELECT * FROM users WHERE username = %s;"
            cursor.execute(query, [username])
            result = cursor.fetchall()
        if result:
            # User with the given email exists
            data = {'rescode': '0001', 'message': 'username found'}
        else:
            # User with the given email does not exist
            data = {'rescode': '0002', 'message': 'User not found'}
            
    except (IntegrityError, ValidationError) as e:
        # Handle any database integrity errors or validation errors
        data = {'rescode': 'error', 'message': str(e)}

    return Response(data)
    
@api_view(['POST'])
def verifyEmail(request):
    email = request.query_params.get('email', '')

    try:
        with connection.cursor() as cursor:
            # Use parameterized query to prevent SQL injection
            query = "SELECT * FROM users WHERE email = %s;"
            cursor.execute(query, [email])
            result = cursor.fetchall()
        if result:
            # User with the given email exists
            data = {'rescode': '0001', 'message': 'Email found'}
        else:
            # User with the given email does not exist
            data = {'rescode': '0002', 'message': 'User not found'}
            
    except (IntegrityError, ValidationError) as e:
        # Handle any database integrity errors or validation errors
        data = {'rescode': 'error', 'message': str(e)}

    return Response(data)
    
@api_view(['POST'])
def changePassword(request):
    email = request.query_params.get('email', '')
    newpassword = request.query_params.get('password', '')

    try:
        with connection.cursor() as cursor:
            # Check if the user exists
            select_query = "SELECT * FROM users WHERE email = %s;"
            cursor.execute(select_query, [email])
            result = cursor.fetchall()

            if result:
                # Update the password for the user
                update_query = "UPDATE users SET password = %s WHERE email = %s;"
                cursor.execute(update_query, [newpassword, email])
                connection.commit()

                data = {'rescode': '0001', 'message': 'Password changed successfully'}
            else:
                # User with the given email does not exist
                data = {'rescode': '0002', 'message': 'User not found'}

    except (IntegrityError, ValidationError) as e:
        # Handle any database integrity errors or validation errors
        data = {'rescode': 'error', 'message': str(e)}

    return Response(data)

@api_view(['POST'])
def createAccount(request):
    username = request.query_params.get('username', '') 
    email = request.query_params.get('email', '')
    password = request.query_params.get('password', '')
    token = TG.generate_token()

    try:
        with connection.cursor() as cursor:
            # Use parameterized query to prevent SQL injection
            query = "INSERT INTO users (username, email, password, Token) VALUES (%s, %s, %s, %s);"
            cursor.execute(query, [username, email, password, token])
            connection.commit()  # Commit changes to the database

        # Check if the user was successfully created
        data = {'rescode': '0001', 'message': 'User created successfully'}

    except IntegrityError as e:
        # Handle unique constraint violation (duplicate username or email)
        data = {'rescode': '0002', 'message': str(e) + ' | Duplicate username or email'}

    except ValidationError as e:
        # Handle validation errors (e.g., invalid email format)
        data = {'rescode': 'error', 'message': str(e)}

    return Response(data)

@api_view(['POST'])
def getProfileData(request):
    token = request.query_params.get('Id', '')

    try:
        with connection.cursor() as cursor:
            # Use parameterized query to prevent SQL injection
            query = "SELECT followers, following, profilePic, username, posts, profileBanner, accType FROM users WHERE id = %s;"
            cursor.execute(query, [token])
            result = cursor.fetchone()

            if result:
                followers, following, profile_pic, username, posts, profileBanner, accType = result
                # Format followers and following
                formatted_followers = format_number(followers)
                formatted_following = format_number(following)

                # User found, return formatted followers, formatted following, profilePic, username, and posts
                data = {
                    'rescode': '0001',
                    'message': 'Profile data retrieved successfully',
                    'followers': formatted_followers,
                    'following': formatted_following,
                    'profilePic': profile_pic,
                    'username': username,
                    'posts': posts,
                  	'profileBanner': profileBanner,
                  	'accType': accType
                }
            else:
                # User not found
                data = {'rescode': '0002', 'message': 'User not found with the provided token'}

    except Exception as e:
        # Handle any other exceptions
        data = {'rescode': 'error', 'message': str(e)}

    return Response(data)

def format_number(number):
    if number < 1000:
        return str(number)
    elif number < 1_000_000:
        return "{:.1f}K".format(number / 1000)
    elif number < 1_000_000_000:
        return "{:.1f}M".format(number / 1_000_000)
    else:
        return "{:.1f}B".format(number / 1_000_000_000)
    
 
@api_view(['POST'])
def getId(request):
    token = request.query_params.get('token', '')

    try:
        with connection.cursor() as cursor:
            # Use parameterized query to prevent SQL injection
            query = "SELECT id FROM users WHERE Token = %s;"
            cursor.execute(query, [token])
            result = cursor.fetchone()

            if result:
                user_id = result[0]  # Extract the id from the result
                data = {
                    'rescode': '0001',
                    'message': 'User ID retrieved successfully',
                    'user_id': user_id
                }
            else:
                # User not found
                data = {'rescode': '0002', 'message': 'User not found with the provided token'}

    except Exception as e:
        # Handle any other exceptions
        data = {'rescode': 'error', 'message': str(e)}

    return Response(data)

@api_view(['POST'])
def getPost(request):
    id = request.query_params.get('id', '')
    offset = int(request.query_params.get('postN', 0))  # Get offset from query parameters

    try:
        with connection.cursor() as cursor:
            # Use parameterized query to prevent SQL injection
            query = "SELECT id, location, Title, description, likes, data FROM posts WHERE author_id = %s ORDER BY id DESC LIMIT 1 OFFSET %s;"
            cursor.execute(query, [id, offset])
            result = cursor.fetchone()

            if result:
                id, location, Title, description, likes, data = result
                likes = format_number(likes)
                data = {
                    'rescode': '0001',
                    'message': 'Post retrieved successfully',
                    'postId': id,
                    'location': location,
                    'Title': Title,
                    'description': description,
                    'likes': likes,
                  	'data': data
                }
            else:
                # Post not found
                data = {'rescode': '0002', 'message': 'Post not found with the provided ID and offset'}

    except Exception as e:
        # Handle any other exceptions
        data = {'rescode': 'error', 'message': str(e)}

    return Response(data)

@api_view(['POST'])
def addLike(request):
    userId = request.query_params.get('userId', '')
    postId = request.query_params.get('postId', '')

    try:
        with connection.cursor() as cursor:
            # Check if the user has already liked the post
            query_check_like = "SELECT * FROM Like_Post_User WHERE User_id = %s AND Post_id = %s;"
            cursor.execute(query_check_like, [userId, postId])
            result = cursor.fetchone()

            if result:
                # User has already liked the post, remove the like
                delete_query = "DELETE FROM Like_Post_User WHERE User_id = %s AND Post_id = %s;"
                cursor.execute(delete_query, [userId, postId])
                
                # Subtract 1 from the "likes" attribute in the "posts" table
                update_likes_query = "UPDATE posts SET likes = likes - 1 WHERE id = %s;"
                cursor.execute(update_likes_query, [postId])

                data = {'rescode': '0001', 'message': 'Like removed successfully'}
            else:
                # User has not liked the post, add a like
                insert_query = "INSERT INTO Like_Post_User (User_id, Post_id) VALUES (%s, %s);"
                cursor.execute(insert_query, [userId, postId])

                # Add 1 to the "likes" attribute in the "posts" table
                update_likes_query = "UPDATE posts SET likes = likes + 1 WHERE id = %s;"
                cursor.execute(update_likes_query, [postId])

                data = {'rescode': '0002', 'message': 'Like added successfully'}

    except Exception as e:
        # Handle any other exceptions
        data = {'rescode': 'error', 'message': str(e)}

    return Response(data)

@api_view(['GET'])
def checkLike(request):
    userId = int(request.GET.get('userId', ''))
    postId = int(request.GET.get('postId', ''))

    try:
        with connection.cursor() as cursor:
            # Check if the user has already liked the post
            query_check_like = "SELECT * FROM Like_Post_User WHERE User_id = %s AND Post_id = %s;"
            cursor.execute(query_check_like, [userId, postId])
            result = cursor.fetchone()

            if result:
                data = {'rescode': '0001', 'message': 'User has liked'}
            else:
                data = {'rescode': '0002', 'message': 'User has not liked'}

    except Exception as e:
        # Handle any other exceptions
        data = {'rescode': 'error', 'message': str(e) + " for ids: " + str(userId) + " and " + str(postId)}

    return Response(data)

@api_view(['POST'])
def addPost(request):
    userId = int(request.query_params.get('userId', ""))
    location = request.query_params.get('location', '')
    title = request.query_params.get('title', '')
    desc = request.query_params.get('desc', '')
    likes = 0

    try:
        with connection.cursor() as cursor:
            # Insert the post into the database
            insert_query = "INSERT INTO posts (author_id, location, Title, description, likes) VALUES (%s, %s, %s, %s, %s);"
            cursor.execute(insert_query, [userId, location, title, desc, likes])
            
            # Update the "posts" attribute in the "users" table
            update_likes_query = "UPDATE users SET posts = posts + 1 WHERE id = %s;"
            cursor.execute(update_likes_query, [userId])

            data = {'rescode': '0001', 'message': 'Post published successfully'}
    except Exception as e:
        # Handle any other exceptions
        data = {'rescode': 'error', 'message': str(e)}

    return Response(data)

@api_view(['POST'])
def editPost(request):
    try:
        postId_str = request.query_params.get('postID', "")
        userId_str = request.query_params.get('userId', "")


        # Check if postId and userId are non-empty strings
        if postId_str and userId_str:
            postId = int(postId_str)
            userId = int(userId_str)
        else:
            raise ValueError("postId and userId must be non-empty integers.")

        location = request.query_params.get('location', '')
        title = request.query_params.get('title', '')
        desc = request.query_params.get('desc', '')
        likes = 0

        try:
            with connection.cursor() as cursor:
                # Insert or update the post in the database
                insert_query = "INSERT INTO posts (id, author_id, location, Title, description, likes) VALUES (%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE location = VALUES(location), Title = VALUES(Title), description = VALUES(description);"
                cursor.execute(insert_query, [postId, userId, location, title, desc, likes])

                data = {'rescode': '0001', 'message': 'Post edited successfully'}
        except Exception as e:
            # Handle any other exceptions
            data = {'rescode': 'error', 'message': str(e)}

    except ValueError as ve:
        # Handle ValueError separately if needed
        data = {'rescode': 'error', 'message': str(ve)}

    return Response(data)
@api_view(['POST'])
def removePost(request):
    data = {}
    
    try:
        postId_str = request.query_params.get('postID', "")
        userId_str = request.query_params.get('userId', "")

        if postId_str and userId_str:
            postId = int(postId_str)
            userId = int(userId_str)
        else:
            raise ValueError("postId and userId must be non-empty integers.")

        try:
            with connection.cursor() as cursor:
                # Corrected DELETE statement
                delete_query = "DELETE FROM posts WHERE id = %s"
                cursor.execute(delete_query, [postId])

                # Update the "posts" attribute in the "users" table
                update_likes_query = "UPDATE users SET posts = posts - 1 WHERE id = %s;"
                cursor.execute(update_likes_query, [userId])

                data = {'rescode': '0001', 'message': 'Post removed successfully'}
        except Exception as e:
            # Handle any other exceptions
            data = {'rescode': 'error', 'message': str(e)}
        finally:
            # Always close the database connection in the 'finally' block
            connection.close()

    except ValueError as ve:
        # Handle ValueError separately if needed
        data = {'rescode': 'error', 'message': str(ve)}

    return Response(data)

@api_view(['POST'])
def getDiscoveryPost(request):
    offset = int(request.query_params.get('postN', 0))  # Get offset from query parameters

    try:
        with connection.cursor() as cursor:
            # Use parameterized query to prevent SQL injection
            query = """
                SELECT posts.id, posts.location, posts.Title, posts.description, posts.likes, posts.data,
                       users.id, users.profilePic, users.username, users.accType
                FROM posts
                INNER JOIN users ON posts.author_id = users.id
                ORDER BY posts.id DESC
                LIMIT 1 OFFSET %s;
            """
            cursor.execute(query, [offset])
            result = cursor.fetchone()

            if result:
                (
                    post_id, location, title, description, likes, post_data,
                    author_id, profile_picture, username,accType
                ) = result
                likes = format_number(likes)
                data = {
                    'rescode': '0001',
                    'message': 'Post retrieved successfully',
                    'postId': post_id,
                    'location': location,
                    'Title': title,
                    'description': description,
                    'likes': likes,
                    'data': post_data,
                    'authorId': author_id,
                    'profilePicture': profile_picture,
                    'username': username,
                  	'accType':accType,
                }
            else:
                # Post not found
                data = {'rescode': '0002', 'message': 'Post not found with the provided offset'}

    except Exception as e:
        # Handle any other exceptions
        data = {'rescode': 'error', 'message': str(e)}

    return Response(data)
@api_view(['POST'])
def addFollower(request):
    userId = request.query_params.get('userId', '')
    follower_id = request.query_params.get('followerId', '')  # Corrected variable name

    try:
        with connection.cursor() as cursor:
            # Check if the user has already liked the post
            query_check_like = "SELECT * FROM followers_following WHERE following_id = %s AND follower_id = %s;"
            cursor.execute(query_check_like, [userId, follower_id])
            result = cursor.fetchone()

            if result:
                # User has already liked the post, remove the like
                delete_query = "DELETE FROM followers_following WHERE follower_id = %s AND following_id = %s;"
                cursor.execute(delete_query, [follower_id, userId])

                # Subtract 1 from the "followers" attribute in the "users" table
                update_likes_query = "UPDATE users SET followers = followers - 1 WHERE id = %s;"
                cursor.execute(update_likes_query, [userId])

                # Subtract 1 from the "following" attribute in the "users" table
                update_likes_query = "UPDATE users SET following = following - 1 WHERE id = %s;"  # Corrected variable name
                cursor.execute(update_likes_query, [follower_id])

                data = {'rescode': '0001', 'message': 'Follower removed successfully'}
            else:
                # User has not liked the post, add a following_id
                insert_query = "INSERT INTO followers_following (follower_id, following_id) VALUES (%s, %s);"
                cursor.execute(insert_query, [follower_id, userId])

                # Add 1 to the "followers" attribute in the "users" table
                update_likes_query = "UPDATE users SET followers = followers + 1 WHERE id = %s;"
                cursor.execute(update_likes_query, [userId])

                # Add 1 to the "following" attribute in the "users" table
                update_likes_query = "UPDATE users SET following = following + 1 WHERE id = %s;"  # Corrected variable name
                cursor.execute(update_likes_query, [follower_id])

                data = {'rescode': '0002', 'message': 'Follower added successfully'}

    except Exception as e:
        # Handle any other exceptions
        data = {'rescode': 'error', 'message': str(e)}

    return Response(data)


@api_view(['GET'])
def checkFollower(request):
    userId = int(request.GET.get('userId', ''))
    followerId = int(request.GET.get('followerId', ''))

    try:
        with connection.cursor() as cursor:
            # Check if the user is already following the follower
            query_check_follower = "SELECT * FROM followers_following WHERE follower_id = %s AND following_id = %s;"
            cursor.execute(query_check_follower, [followerId, userId])
            result = cursor.fetchone()

            if result:
                data = {'rescode': '0001', 'message': 'User is following'}
            else:
                data = {'rescode': '0002', 'message': 'User is not following'}

    except Exception as e:
        # Handle any other exceptions
        data = {'rescode': 'error', 'message': str(e) + " for ids: " + str(userId) + " and " + str(followerId)}

    return Response(data)

@api_view(['POST'])
def changeProfile(request):
    user_id = int(request.data.get('userId', ''))

    pfp_file = request.FILES.get('pfp', None)
    pfb_file = request.FILES.get('pfb', None)

    try:
            # Save profile picture
        with open(os.path.join(base_dir, pfp_name), 'wb') as pfp_file_output:
            for chunk in pfp_file.chunks():
                pfp_file_output.write(chunk)

        # Save profile banner
        with open(os.path.join(base_dir, pfb_name), 'wb') as pfb_file_output:
            for chunk in pfb_file.chunks():
                pfb_file_output.write(chunk)

        # Now update the database with the local paths
        pfp_local_path = os.path.join(base_dir, pfp_name)
        pfb_local_path = os.path.join(base_dir, pfb_name)

        with connection.cursor() as cursor:
            query_change_profile_picture = "UPDATE auth_user SET profilePic = %s, profileBanner = %s WHERE id = %s"
            cursor.execute(query_change_profile_picture, [pfp_local_path, pfb_local_path, user_id])
            connection.commit()  # Commit the changes to the database
            result = cursor.rowcount  # Check the number of affected rows

            if result > 0:
                data = {'rescode': '0001', 'message': 'Profile updated'}
            else:
                data = {'rescode': '0002', 'message': 'Profile not updated. User not found or no changes made.'}

    except Exception as e:
        # Handle any other exceptions
        data = {'rescode': 'error', 'message': f'An error occurred while processing the request: {str(e)}'}

    # Set CORS headers
    response = Response(data)
    response = Response(data)
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Credentials'] = 'true'
    response['Access-Control-Allow-Headers'] = 'content-type'
    response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    
    return response

@api_view(['GET'])
def searchUsername(request):
    input_username = request.GET.get('username', '')

    try:
        with connection.cursor() as cursor:
            # Search for usernames in the database that contain the input, limit to 5 results
            query_search_username = (
                "SELECT id, username, profilePic FROM users WHERE username LIKE %s LIMIT 5;"
            )
            cursor.execute(query_search_username, ['%' + input_username + '%'])
            results = cursor.fetchall()

            if results:
                # Extract the relevant fields from the results
                matching_user_data = [
                    {'id': result[0], 'username': result[1], 'profilePic': result[2]} 
                    for result in results
                ]
                data = {'rescode': '0001', 'message': 'User data found', 'users': matching_user_data}
            else:
                data = {'rescode': '0002', 'message': 'No matching users found'}

    except Exception as e:
        # Handle any other exceptions
        data = {'rescode': 'error', 'message': str(e)}

    return Response(data)

